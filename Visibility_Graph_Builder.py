# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 19:56:41 2022

@author: Emmanuel Rosa & Yarier Herrera
"""


##########################
##Visibility Graph Builder
##########################

bl_info = {
    "name": "Visibility Graph Builder",
    "author": "Emmanuel Rosa & Yarier Herrera",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "File > Import-Export",
    "description": "Import a time series (data) to create a visibility graph",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
import csv


##########################
##Building of the graph
##########################

def Graph_Builder(file, columna):

    import pandas as pd
    from ts2vg import NaturalVG
    import networkx as nx
    import numpy as np
    import matplotlib as mpl
    
    df= pd.read_csv(file)
    
   
    def colors_df(df):

        quantiles=df.quantile([.25, .5, .75], axis = 0) 
        quantiles=quantiles.values.tolist()
        Q1= quantiles[0][0]
        Q2= quantiles[1][0]
        Q3= quantiles[2][0]
        
        Quantiles_list=[Q1,Q2,Q3]
        
        df.columns = range(df.columns.size)
        
        
        df['Colors']=0        
        df['Colors'][df[1].between(Q1,Q2)] = "Blue"   
        df['Colors'][df[1].le(Q1)] = "Red"      
        df['Colors'][df[1].between(Q2,Q3)] = "Orange"  
        df['Colors'][df[1].gt(Q3)] = "Green"     
        
        df.columns = range(df.columns.size)

        return df,Quantiles_list 
                

    df,Quantiles=colors_df(df)

    Quantiles= np.array(Quantiles)


    mapname = "winter"




    cmap = mpl.cm.get_cmap(mapname, Quantiles.shape[0])
    norm = mpl.colors.Normalize(vmin=Quantiles.min(), vmax=Quantiles.max())


    
    g = NaturalVG()
    df.columns = range(df.columns.size)
    g.build(df[columna-1])
    
    edges = g.edges


    nxg = g.as_networkx()


    pos = nx.spring_layout(nxg,dim=3,seed=18)

    dfPos= pd.DataFrame.from_dict(pos)
    dfPos= dfPos.T

    dfPos= dfPos.rename(columns={0: "x", 1: "y",2:'z'})

    xs=[]
    ys=[]

    for i in range(len(edges)):
        for j in range(2):
            if j == 0:
                xs.append(edges[i][j])
                
            else:
                ys.append(edges[i][j])
        
        
    if len(dfPos) > 100:
        dfPos=dfPos*5
        

     
    dfPos_T =dfPos.T

    dicts_edges = {}

    for g in range(len(xs)):
            dicts_edges[(xs[g],ys[g])] = dfPos_T[xs[g]], dfPos_T[ys[g]]
        

    edgesPos = pd.DataFrame.from_dict(dicts_edges)
    edgesPos= edgesPos.T



    import bpy 

    def setRenderSize():
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1920

    bpy.ops.object.delete(use_global=False)

    setRenderSize()


    colores= cmap(norm(Quantiles))

    mats = []

    for i in range(len(colores)):
        mats.append(bpy.data.materials.new("mat" + str(i)))
        mats[i].diffuse_color = colores[i]


    for i in range(len(dfPos)):
        
        c1 = dfPos["x"][i]
        c2 = dfPos["y"][i]
        c3 = dfPos["z"][i]

        color = df.iloc[:,-1][i]
        
        bpy.ops.mesh.primitive_uv_sphere_add(location=(c1,c2,c3),scale=(0.04,0.04,0.04))
        
        
        bpy.ops.object.shade_smooth()
        
        obj = bpy.context.object 
        
        if color == "Red":
            obj.active_material = mats[0]
        elif color == "Green":
            obj.active_material = mats[1]  
                 
        else:
            obj.active_material = mats[2]

      
    import math
        
    def cylinder_between(x1, y1, z1, x2, y2, z2, r,dfPos):

      dx = x2 - x1
      dy = y2 - y1
      dz = z2 - z1    
      dist = math.sqrt(dx**2 + dy**2 + dz**2)

      bpy.ops.mesh.primitive_cylinder_add(
          radius = r, 
          depth = dist,
          location = (dx/2 + x1, dy/2 + y1, dz/2 + z1)   
      ) 

      phi = math.atan2(dy, dx) 
      theta = math.acos(dz/dist) 

      bpy.context.object.rotation_euler[1] = theta 
      bpy.context.object.rotation_euler[2] = phi 
      
      
      
      colores = [(0.0,0.0,0.0,1.0)]

      mats = []

      for i in range(len(colores)):
            mats.append(bpy.data.materials.new("mat" + str(i)))
            mats[i].diffuse_color = colores[i]
        
        
      bpy.ops.object.shade_smooth()

      obj = bpy.context.object 


      obj.active_material = mats[0]
      
    for i in range(len(edgesPos)):
          
         if len(dfPos) > 100:
             radio = 0.001
             
         else:
             radio=0.01
    
    
    
         cylinder_between(edgesPos.iloc[i][0].x,edgesPos.iloc[i][0].y,edgesPos.iloc[i][0].z,
                           edgesPos.iloc[i][1].x,edgesPos.iloc[i][1].y,
                           edgesPos.iloc[i][1].z,radio,dfPos)
         


##########################
##Reading csv file
##########################

def read_csv_data(context, filepath, data_fields, encoding='latin-1', delimiter=",", leading_liens_to_discard=0,chosen_column=2):

 
    report_type = 'INFO'
    report_message = ""

    mesh = bpy.data.meshes.new(name="csv_data")

    add_data_fields(mesh, data_fields)
    

    
    with open(filepath, 'r', encoding=encoding, newline='') as csv_file:
        
        discarded_leading_lines = 0
        while(discarded_leading_lines < leading_liens_to_discard):
            line = csv_file.readline()
            discarded_leading_lines = discarded_leading_lines + 1

        csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

        error_message = ""
        i=0
        try:
            for row in csv_reader:
                for data_field in data_fields:
                    value = row[data_field.name]
                    if(data_field.dataType == 'FLOAT'):
                        value = float(value)
                    elif(data_field.dataType == 'INT'):
                        value = int(value)
                    elif(data_field.dataType == 'BOOLEAN'):
                        value = bool(value)
                    row[data_field.name] = value
                
                mesh.vertices.add(1)
                mesh.update()

                for data_field in data_fields:
                    mesh.attributes[data_field.name if data_field.name else "empty_key_string"].data[i].value = row[data_field.name]

                mesh.vertices[i].co = (0.01 * i,0.0,0.0) 
                i = i+1
        except ValueError as e:
            error_message = repr(e)
            report_type = 'WARNING'
        except KeyError as e:
            error_message = repr(e)
            report_type = 'WARNING'

        csv_file.close()

        mesh.update()
        mesh.validate()

        file_name = bpy.path.basename(filepath)
        object_name = bpy.path.display_name(file_name)

        report_message = "{message}\n{error_message}".format(message=report_message, error_message=error_message)

    return report_message, report_type


def add_data_fields(mesh, data_fields):
    for data_field in data_fields:
        mesh.attributes.new(name=data_field.name if data_field.name else "empty_key_string", type=data_field.dataType, domain='POINT')


class SPREADSHEET_UL_data_fields(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(data=item, property="name", text="")
            layout.prop(data=item, property="dataType", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(data=item, property="name", text="")
            layout.prop(data=item, property="dataType", text="")



class DataFieldPropertiesGroup(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(
        name="Field Name",
        description="The name of the field to import",
        default="",
    )

    dataType: bpy.props.EnumProperty(
        name="Field Data Type",
        description="Choose Data Type",
        items=(
            ('FLOAT', "Float", "Floating-point value"),
            ('INT', "Integer", "32-bit integer"),
            ('BOOLEAN', "Boolean", "True or false"),
        ),
        default='FLOAT',
    )

##########################
##Importation of the file
##########################


class ImportSpreadsheetData(bpy.types.Operator, ImportHelper):
    """Import data to Spreadsheet"""
    bl_idname = "import.spreadsheet"  
    bl_label = "Import Spreadsheet"

    filter_glob: bpy.props.StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        maxlen=255,  
    )

    data_fields: bpy.props.CollectionProperty(
        type=DataFieldPropertiesGroup,
        name="Field names",
        description="All the fields that should be imported",
        options={'HIDDEN'},
    )

    active_data_field_index: bpy.props.IntProperty(
        name="Index of data_fields",
        default=0,
        options={'HIDDEN'},
    )

    array_name: bpy.props.StringProperty(
        name="Array name",
        description="The name of the array to import",
        default="",
        options={'HIDDEN'},
    )
    
    json_encoding: bpy.props.StringProperty(
        name="Encoding",
        description="Encoding of the JSON File",
        default="utf-8-sig",
        options={'HIDDEN'},
    )

    csv_delimiter: bpy.props.StringProperty(
        name="Delimiter",
        description="A one-character string used to separate fields.",
        default=",",
        maxlen=1,
        options={'HIDDEN'},
    )

    csv_leading_lines_to_discard: bpy.props.IntProperty(
        name="Discard leading lines",
        description="Leading lines to discard",
        default=0,
        min=0,
        options={'HIDDEN'},
    )

    csv_encoding: bpy.props.StringProperty(
        name="Encoding",
        description="Encoding of the CSV File",
        default="latin-1",
        options={'HIDDEN'},
    
    )
    
       
    chosen_column: bpy.props.IntProperty(
        name="Column to be selected from the file",
        description="Column which will be chosen from the file",
        default=2,
        options={'HIDDEN'},
    )


    def draw(self, context):
        layout = self.layout
        layout.label(text="Import Spreadsheet Options")

    def execute(self, context):
       
        if(self.filepath.endswith('.csv')):
            report_message, report_type = read_csv_data(context, self.filepath, self.data_fields, self.csv_encoding, self.csv_delimiter, self.csv_leading_lines_to_discard,self.chosen_column)
        
        self.report({report_type}, report_message)
        
        Graph_Builder(self.filepath, self.chosen_column)
        
        
        return {'FINISHED'}
    
    
    

class AddDataFieldOperator(bpy.types.Operator):
    bl_idname = "import.spreadsheet_field_add"
    bl_label = "Add field"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        item = operator.data_fields.add()

        operator.active_data_field_index = len(operator.data_fields) - 1
        
        return {'FINISHED'}

class RemoveDataFieldOperator(bpy.types.Operator):
    bl_idname = "import.spreadsheet_field_remove"
    bl_label = "Remove field"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        index = operator.active_data_field_index
        operator.data_fields.remove(index)
        operator.active_data_field_index = min(max(0,index - 1), len(operator.data_fields)-1)
        return {'FINISHED'}



##########################
##File options
##########################


class SPREADSHEET_PT_csv_options(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "CSV Import Options"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_OT_spreadsheet" and operator.filepath.lower().endswith('.csv')

    def draw(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        layout = self.layout
        layout.prop(data=operator, property="csv_delimiter")
        layout.prop(data=operator, property="csv_leading_lines_to_discard")
        layout.prop(data=operator, property="csv_encoding")
        layout.prop(data=operator, property="chosen_column")


class SPREADSHEET_PT_field_names(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Field Names"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_OT_spreadsheet"

    def draw(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        layout = self.layout

        rows = 2
        filed_names_exist = bool(len(operator.data_fields) >= 1)
        if filed_names_exist:
            rows = 4

        row = layout.row()
        row.template_list("SPREADSHEET_UL_data_fields", "", operator, "data_fields", operator, "active_data_field_index", rows=rows)

        col = row.column(align=True)
        col.operator(AddDataFieldOperator.bl_idname, icon='ADD', text="")
        col.operator(RemoveDataFieldOperator.bl_idname, icon='REMOVE', text="")
        
blender_classes = [
    SPREADSHEET_UL_data_fields,
    DataFieldPropertiesGroup,
    ImportSpreadsheetData,
    SPREADSHEET_PT_field_names,
    SPREADSHEET_PT_csv_options,
    AddDataFieldOperator,
    RemoveDataFieldOperator,
]




######################################
##Menu for the importation of the file
######################################


def menu_func_import(self, context):
    self.layout.operator(ImportSpreadsheetData.bl_idname, text="Visibility Graph (.csv)")

def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    

        
        
        