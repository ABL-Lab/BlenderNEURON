import bpy, random, numpy
from blenderneuron.blender import BlenderNodeClass

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty,
                       FloatProperty,
                       FloatVectorProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)


class CUSTOM_NEURON_IU_Root(PropertyGroup, BlenderNodeClass):
    name = StringProperty()
    index = IntProperty()
    hash = StringProperty()

    def on_selected_updated(self, context):
        new_group = self.node.ui_properties.group.node_group if self.selected else None
        self.node.root_index[self.hash].add_to_group(new_group)

    selected = BoolProperty(default=False, update=on_selected_updated)

class CUSTOM_NEURON_UI_Root_Group(PropertyGroup, BlenderNodeClass):

    @property
    def node_group(self):
        return self.node.groups[self.name]

    # The following two methods are helper methods for setting node group properties via the GUI
    def get_prop(prop):
        def get(self):
            return getattr(self.node_group, prop)
        return get

    def set_prop(prop):
        def set(self, value):
            setattr(self.node_group, prop, value)
        return set

    index = IntProperty(get=get_prop("index"), set=set_prop("index"))
    selected = BoolProperty(default=True, get=get_prop("selected"), set=set_prop("selected"))

    root_entries = CollectionProperty(type=CUSTOM_NEURON_IU_Root)
    root_entries_index = IntProperty()

    record_activity = BoolProperty(
        default=True,
        get=get_prop("record_activity"),
        set=set_prop("record_activity"),
        description="Imports the recorded values from the selected variable (based on granularity) "
                    "and shows it at variation in Blender segment brightness")

    import_synapses = BoolProperty(
        default=True,
        get=get_prop("import_synapses"),
        set=set_prop("import_synapses"),
        description="Imports synaptic connections and visually represents them in Blender"
    )

    recording_period = FloatProperty(
        default=1.0,
        min=0.0,
        get=get_prop("recording_period"),
        set=set_prop("recording_period"),
        description="How often to collect the recording variable during simulation (ms)"
    )

    record_variable = StringProperty(
        default="v",
        get=get_prop("record_variable"),
        set=set_prop("record_variable"),
        description="The NEURON section variable to record"
                    " (e.g. 'v' of soma(0.5).v) and display as segment brigthness in Blender"
    )

    gran2int = {
        "Group": 3,
        "Cell": 2,
        "Section": 1,
        "3D Segment": 0
    }

    int2gran = dict(reversed(item) for item in gran2int.items())

    def get_gran_prop(prop):
        def get(self):
            return self.gran2int[getattr(self.node_group, prop)]
        return get

    def set_gran_prop(prop):
        def set(self, value):
            setattr(self.node_group, prop, self.int2gran[value])
        return set

    recording_granularity = bpy.props.EnumProperty(
        items=[
            ('Group', 'Cell Group', 'Coarsest. Reports the mean value across all selected cell somas (root segments)', 3),
            ('Cell', 'Soma', 'Reports the value at each selected cell soma (root)', 2),
            ('Section', 'Section', 'Reports values at each selected cell section', 1),
            ('3D Segment', '3D Segment', 'Finest. Reports values between each cell section 3D point', 0),
        ],
        name="Recording granularity",
        description="The granularity used to record from selected cells. Finest recording "
                    "granularity requires more time and memory, coarsest less so.",
        default='Section',
        get=get_gran_prop("recording_granularity"),
        set=set_gran_prop("recording_granularity")
    )

    interaction_granularity = bpy.props.EnumProperty(
        items=[
            ('Group', 'Cell Group', 'Coarsest. The group of selected cells is represented as '
                                'one object in Blender', 3),
            ('Cell', 'Cell', 'Each cell is represented as a Blender object', 2),
            ('Section', 'Section', 'Finest. Each cell section is represented as a Blender object', 1),
        ],
        name="Interaction granularity",
        description="The granularity used to represent selected cells in Blender. "
                    "Finer granularity allows interaction with smaller parts of cells, "
                    "but can result in performance issues if the number of cells/sections "
                    "is large. Coarser interativity increases performance for larger models.",
        default='Cell',
        get=get_gran_prop("interaction_granularity"),
        set=set_gran_prop("interaction_granularity")
    )



    # TODO move this to a map property
    smooth_sections = BoolProperty(
        default=True,
        description="Whether to render sections as smooth bezier curves, instead of straight lines. "
                    "True results in more visually appealing morphology, but requires more polygons."
    )

    # TODO move this to a map property
    spherize_soma_if_DeqL = BoolProperty(
        default=True,
        description="Whether to display a soma section with diameter ~= length as a sphere in Blender"
    )

    # TODO move this to a map property
    as_lines = BoolProperty(
        default=False,
        description="Whether to display sections as line segments (no radius). This is fast, but cannot be rendered."
    )

    # TODO move this to a map property
    segment_subdivisions = IntProperty(
        default=3,
        min=2,
        description="Number of linear subdivisions to use when displaying a section. Higher results in smooth-"
                    "looking section curvature, but requires more polygons."
    )

    # TODO move this to a map property
    circular_subdivisions = IntProperty(
        default=12,
        min=5,
        description="Number of linear subdivisions to use when displaying a section. Higher results in smooth-"
                    "looking section curvature."
    )

class CUSTOM_NEURON_SimulatorSettings(BlenderNodeClass, PropertyGroup):

    def to_neuron(self, context=None):
        self.client.set_sim_params({
            "tstop": self.neuron_tstop,
            "dt": self.time_step,
            "atol": self.abs_tolerance,
            "celsius": self.temperature,
            "cvode": self.integration_method,
        })

    def from_neuron(self):
        client = self.client

        if client is None:
            return

        params = client.get_sim_params()

        self.neuron_tstop = params["tstop"]
        self.time_step = params["dt"]
        self.abs_tolerance = params["atol"]
        self.temperature = params["celsius"]
        self.integration_method = str(int(float(params["cvode"])))

    neuron_tstop = FloatProperty(
        min = 0,
        default = 100,
        description="The simulation stop time (e.g. h.tstop) in ms",
        update=to_neuron
    )

    time_step = FloatProperty(
        default=0.25,
        min = 0,
        precision=3,
        description="The time step used by the Fixed Step integrator (in ms)",
        update=to_neuron
    )

    abs_tolerance = FloatProperty(
        default=0.001,
        min=0,
        precision=5,
        description="The absolute tolerace used by the Variable Step (CVODE) integrator",
        update=to_neuron
    )

    temperature = FloatProperty(
        default=6.3,
        description="The simulation temperature in degrees Celsius",
        update=to_neuron
    )

    integration_method = bpy.props.EnumProperty(
        items=[
            ('0', 'Fixed Step', 'Each simulation step is constant size'),
            ('1', 'Variable Step (CVODE)', 'Each simulation step is variable depending '
                                           'on the rate of state changes'),
        ],
        name="Integrator",
        description="Variable step tends to be faster for single cells and low firing "
                    "rates. Fixed step tends to be faster for networks and high firing rates.",
        default='1',
        update=to_neuron
    )

class CUSTOM_BlenderNEURON(PropertyGroup):

    groups_index = IntProperty()

    groups = CollectionProperty(
        type=CUSTOM_NEURON_UI_Root_Group
    )

    @property
    def group(self):
        """
        :return: The currently highlighted UI group
        """
        return self.groups[self.groups_index]

    simulator_settings = PointerProperty(
        type=CUSTOM_NEURON_SimulatorSettings
    )

def register():
    bpy.types.Scene.BlenderNEURON = PointerProperty(type=CUSTOM_BlenderNEURON)

def unregister():
    del bpy.types.Scene.BlenderNEURON