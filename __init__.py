#-------------------------------------------------
#-__INIT__.py
#-------------------------------------------------

bl_info = {
    "name": "XTD Tools 2025",
    "description": "Advanced batch processing and utility tools for Blender.",
    "author": "User",
    "version": (1, 0, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Tools > XTD Tools 2025",
    "category": "Object"
}

from .global_settings import *

def import_and_register_modules():
    os.system("cls")
    print("Install XTD Tools...")
    
    global registered_classes, global_functions, registered_properties, global_settings

    global_settings = importlib.import_module(".global_settings", package=__name__)
    importlib.reload(global_settings)

    for panel in panels:
        proper_name = f"show_{panel}"
        print(proper_name)
        if not hasattr(bpy.types.Scene, proper_name):
            print("Adding property: " + proper_name)
            setattr(bpy.types.Scene, proper_name, bpy.props.BoolProperty(
                name=f"Show {panel}",
                description=f"Toggle visibility of the {panel} panel",
                default=True,
                update=make_update_callback(panel)
            ))

    for panel_name in panels:
        module = importlib.import_module(f".{panel_name}", package=__name__)
        importlib.reload(module)

        for name, cls in inspect.getmembers(module, inspect.isclass):
            if hasattr(cls, 'bl_idname') and hasattr(cls, 'bl_label'):
                if issubclass(cls, bpy.types.Panel) and cls != bpy.types.Panel:
                    if cls not in registered_classes:
                        registered_classes.append(cls)
                elif issubclass(cls, bpy.types.PropertyGroup) and cls != bpy.types.PropertyGroup:
                    if cls not in registered_classes:
                        registered_classes.append(cls)
                elif hasattr(global_settings, "XTDToolsOperator") and issubclass(cls, global_settings.XTDToolsOperator) and cls != global_settings.XTDToolsOperator:
                    if cls not in registered_classes:
                        registered_classes.append(cls)

        for name, value in inspect.getmembers(module):
            if isinstance(value, (bpy.types.Panel, bpy.types.Operator, bpy.types.PropertyGroup)):
                if value not in registered_classes:
                    registered_classes.append(value)

        for name, prop in registered_properties:
            if not hasattr(bpy.types.Scene, name):
                setattr(bpy.types.Scene, name, prop)

        for name, func in inspect.getmembers(module, inspect.isfunction):
            global_functions[name] = func

        setattr(module, "global_settings", global_settings)

    for panel_name in panels:
        module = importlib.import_module(f".{panel_name}", package=__name__)
        for func_name, func in global_functions.items():
            setattr(module, func_name, func)

    print("Ready! Let's rock!")

def register():
    import_and_register_modules()
    
    for cls in registered_classes:
        bpy.utils.register_class(cls)

    for name, prop in registered_properties:
        if not hasattr(bpy.types.Scene, name): 
            setattr(bpy.types.Scene, name, prop)


def unregister():
    global registered_properties
    
    for cls in reversed(registered_classes):
        bpy.utils.unregister_class(cls)
    registered_classes.clear()
    
    for name, _ in registered_properties:
        if hasattr(bpy.types.Scene, name):
            delattr(bpy.types.Scene, name)
    registered_properties.clear()

if __name__ == "__main__":
    register()