from ..Script import Script
import math
class ProPurge(Script):
    version = "1.03"
    currentOffset = 0
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"Pro Purge v.(""" + self.version + """)",
            "key":"ProPurge",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "_direction":
                {
                    "label": "Purge Direction",
                    "description": "Which direction to purge.",
                    "unit": "Side",
                    "type": "enum",
                    "options": {"vertical": "Vertical Y", "horizontal": "Horizontal X"},
                    "default_value": "vertical" 
                },
                "_margin":
                {
                    "label": "Margin",
                    "description": "How far from edge should the purge line parallel",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 10
                },
                "_inset":
                {
                    "label": "Inset",
                    "description": "How far from start edge should the purge line start",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 10
                },
                "_length":
                {
                    "label": "Purge Length",
                    "description": "How long should the purge line be",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 200
                },
                "_height":
                {
                    "label": "Purge Layer Height",
                    "description": "How tall should the purge layer be",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.3
                },
                "_flow":
                {
                    "label": "Flow",
                    "description": "Amount of filament to purge per line (0 to calculate)",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "_speed":
                {
                    "label": "Purge Speed",
                    "description": "The speed to print the purge pattern",
                    "unit": "mm/minute",
                    "type": "float",
                    "default_value": 1500,
                    "minimum_value_warning": 500,
                    "maximum_value_warning": 3000,
                    "minimum_value": 100
                },
                "_strokes":
                {
                    "label": "Purge Stroke Count",
                    "description": "How many purge lines to run",
                    "unit": "wipes",
                    "type": "int",
                    "default_value": 2,
                    "minimum_value_warning": 1,
                    "maximum_value_warning": 5,
                    "minimum_value": 1,
                    "maximum_value": 50
                },
                "_spacing":
                {
                    "label": "Line Spacing / Line Width",
                    "description": "How far to move between purge lines, and how wide to make it. Used to calculate Flow.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.5,
                    "minimum_value_warning": 0.3,
                    "maximum_value_warning": 1,
                    "minimum_value": 0.2,
                    "maximum_value": 2
                },
                "_zhop":
                {
                    "label": "Z Hop",
                    "description": "How high to lift the nozzle after purging",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 2,
                    "minimum_value_warning": 0.1,
                    "maximum_value_warning": 10,
                    "minimum_value": 0,
                    "maximum_value": 50
                },
                "_wipe":
                {
                    "label": "Wipe After Purge",
                    "description": "Whether to wipe the nozzle on the purge line to prevent stringing. Minimum 2 strokes required.",
                    "unit": "mm",
                    "type": "bool",
                    "default_value": true,
                    "enabled": "_strokes > 1"
                },
                "_filamentDiameter":
                {
                    "label": "Filament Diameter",
                    "description": "The diameter of the filament, for calculated flow values",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 1.75,
                    "enabled": "_flow == 0"
                },
                "_flowPercent":
                {
                    "label": "Calculated Flow Percentage",
                    "description": "After calculating flow, apply this percentage modifier.",
                    "unit": "%",
                    "type": "float",
                    "default_value": 100,
                    "enabled": "_flow == 0",
                    "minimum_value_warning": 50,
                    "maximum_value_warning": 150,
                    "minimum_value": 10,
                    "maximum_value": 300
                },
                "_blob":
                {
                    "label": "Blob Purge",
                    "description": "Whether to do a blob purge",
                    "type": "bool",
                    "default_value": false
                },
                "_blobX":
                {
                    "label": "Blob X Position",
                    "description": "Where to put the blob, horizontally",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5,
                    "enabled": "_blob == 1"
                },
                "_blobY":
                {
                    "label": "Blob Y Position",
                    "description": "Where to put the blob, vertically",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5,
                    "enabled": "_blob == 1"
                },
                "_blobZStart":
                {
                    "label": "Blob Z Start",
                    "description": "What height to start blobbing at",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.2,
                    "enabled": "_blob == 1"
                },
                "_blobZEnd":
                {
                    "label": "Blob Z End",
                    "description": "What height to stop blobbing at",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 1,
                    "enabled": "_blob == 1"
                },
                "_blobFlow":
                {
                    "label": "Blob Flow",
                    "description": "The amount of filament used to make the blob",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 50,
                    "enabled": "_blob == 1"
                }
            }
        }"""

    #Extrusion Calculator: E value = diameter*layer height* distance / filament cross sectional area
    def calculateExtrusion(self, LineWidth_, LayerHeight_, Distance_, FilamentDiameter_, FlowPercent_ = 100):
        return (LineWidth_ * LayerHeight_ * Distance_ / (math.pow(FilamentDiameter_ / 2, 2) * math.pi)) * FlowPercent_ / 100

    # distance is the hypotenuse measurement
    def distance(self, StartX, StartY, EndX, EndY):
        return math.abs(math.sqrt(math.pow(StartX - EndX, 2) + math.pow(StartY - EndY, 2)))

    # Generate a blob to purge filament
    def buildBlobGCode(self, X, Y, StartZ, EndZ, Flow, Speed, Zhop):
        purgeGcode = "; BEGIN PRO PURGE BLOB\n"
        purgeGcode += "G92 E0 ; RESET EXTRUDER \n"
        purgeGcode += "G1 X" + str(X) + " Y" + str(Y) + " Z" + str(StartZ)
        purgeGcode += " F" + str(Speed*2) + " ; Move to blob start position \n"
        purgeGcode += "G1 X" + str(X) + " Y" + str(Y) + " Z" + str(EndZ)
        purgeGcode += " F" + str(Speed) + " E" + str(Flow) + "\n"
        purgeGcode += "G1 Z" + str(Zhop)
        purgeGcode += " ; PRO PURGE END BLOB\n"
        return purgeGcode

    def buildGCode(self, Direction_, Margin_, Inset_, Length_, Height_, Flow_, Speed_, Zhop_, Strokes_, Spacing_, Wipe_, FilamentDiameter_, FlowPercent_):
        global currentOffset
        if Flow_ == 0:
            Flow_ = self.calculateExtrusion(Spacing_, Height_, Length_, FilamentDiameter_, FlowPercent_)
        totalExtrude = 0
        strokeAxis = "Y"
        lineAxis = "X"
        if (Direction_ == "horizontal"):
            strokeAxis = "X"
            lineAxis = "Y"
        purgeGcode = "; BEGIN PRO PURGE \n"
        purgeGcode += "G92 E0 ; RESET EXTRUDER \n"
        purgeGcode += "G1 " + lineAxis + str(Margin_ + currentOffset) + " " + strokeAxis + str(Inset_) 
        purgeGcode += " F" + str(Speed_*2) + " ; Move to purge start position \n"
        purgeGcode += "G1 Z" + str(Zhop_) + "F" + str(Speed_) + " ; Move to Z Hop Height \n"
        for thisStroke in range(0, Strokes_):
            # Print purge line one way
            purgeGcode += "G1 " + lineAxis + str(Margin_ + currentOffset) + " " + strokeAxis + str(Inset_) 
            purgeGcode += " Z" + str(Height_) + " F" + str(Speed_*2)
            # purgeGcode += " ; PRO PURGE Move to start of line " + str(thisStroke + 1)
            purgeGcode += "\n"
            totalExtrude += Flow_
            purgeGcode += "G1 " + lineAxis + str(Margin_ + currentOffset) + " " + strokeAxis + str(Inset_ + Length_) 
            purgeGcode += " Z" + str(Height_) + " F" + str(Speed_) + " E" + str(totalExtrude)
            #purgeGcode += " ; PRO PURGE Draw Line " + str(thisStroke + 1)
            purgeGcode += "\n"
            currentOffset += Spacing_
            purgeGcode += "G1 " + lineAxis + str(Margin_ + currentOffset) + " " + strokeAxis + str(Inset_ + Length_) 
            purgeGcode += " Z" + str(Height_) + " F" + str(Speed_ * 2)
            #purgeGcode += " ; PRO PURGE Move to side " + str(thisStroke + 1)
            purgeGcode += "\n"
            totalExtrude += Flow_
            purgeGcode += "G1 " + lineAxis + str(Margin_ + currentOffset) + " " + strokeAxis + str(Inset_) 
            purgeGcode += " Z" + str(Height_) + " F" + str(Speed_) + " E" + str(totalExtrude)
            #purgeGcode += " ; PRO PURGE Draw Return Line " + str(thisStroke + 1)
            purgeGcode += "\n"
            currentOffset += Spacing_
        purgeGcode += "G92 E0 ; RESET EXTRUDER \n"
        if Wipe_:
            purgeGcode += "G1 " + lineAxis + str(Margin_ + currentOffset - (Spacing_ * 2)) + " " + strokeAxis + str(Inset_) 
            purgeGcode += " Z" + str(Height_) + " F" + str(Speed_ * 2)
            purgeGcode += " ; WIPE " + str(thisStroke + 1) + "\n"
        purgeGcode += "G1 Z" + str(Zhop_) + "F" + str(Speed_) + " ; Move Z Axis Up \n"
        purgeGcode += "; END PRO PURGE \n"
        return purgeGcode

    def execute(self, data):
        # used to keep track of where the nozzle is offset to between purges
        global currentOffset
        _Direction = self.getSettingValueByKey("_direction")
        _Margin = self.getSettingValueByKey("_margin")
        _Inset = self.getSettingValueByKey("_inset")
        _Length = self.getSettingValueByKey("_length")
        _Height = self.getSettingValueByKey("_height")
        _Flow = self.getSettingValueByKey("_flow")
        _Speed = self.getSettingValueByKey("_speed")
        _Zhop = self.getSettingValueByKey("_zhop")
        _Strokes = self.getSettingValueByKey("_strokes")
        _Spacing = self.getSettingValueByKey("_spacing")
        _Wipe = self.getSettingValueByKey("_wipe")
        _FilamentDiameter = self.getSettingValueByKey("_filamentDiameter")
        _FlowPercent = self.getSettingValueByKey("_flowPercent")
        #Blob Specific Settings
        _Blob = self.getSettingValueByKey("_blob")
        _BlobX = self.getSettingValueByKey("_blobX")
        _BlobY = self.getSettingValueByKey("_blobY")
        _BlobZStart = self.getSettingValueByKey("_blobZStart")
        _BlobZEnd = self.getSettingValueByKey("_blobZEnd")
        _BlobFlow = self.getSettingValueByKey("_blobFlow")
        currentOffset = 0
        purge_gcode = self.buildGCode(_Direction, _Margin, _Inset, _Length, _Height, _Flow, _Speed, _Zhop, _Strokes, _Spacing, _Wipe, _FilamentDiameter, _FlowPercent)
        if _Blob:
            blob_gcode = self.buildBlobGCode(_BlobX, _BlobY, _BlobZStart, _BlobZEnd, _BlobFlow, _Speed, _Zhop)
            purge_gcode = blob_gcode + purge_gcode;
        # Find the beginning of the print and insert the purge code there
        for layer in data:
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:0" in line:
                    index = data.index(layer)
                    layer = purge_gcode + layer
                    data[index] = layer
                    return data
        return data