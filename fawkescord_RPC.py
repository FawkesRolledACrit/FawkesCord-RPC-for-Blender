"""
Fawkescord Rich Presence for Blender
=====================================
A Blender addon that displays your Blender activity on Discord with accurate time tracking.

Author: Fawkes
Version: 1.3.1
License: MIT
"""

bl_info = {
    "name": "Fawkescord Rich Presence",
    "author": "Fawkes",
    "version": (1, 3, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Fawkescord",
    "description": "Show Blender activity on Discord with time tracking",
    "category": "System",
}

import bpy  # type: ignore
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Attempt to import pypresence (Discord RPC library)
try:
    from pypresence import Presence  # type: ignore
    PYPRESENCE_AVAILABLE = True
except ImportError:
    # Fallback: Try adding user site-packages to path
    import sys
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.append(user_site)
    
    try:
        from pypresence import Presence  # type: ignore
        PYPRESENCE_AVAILABLE = True
    except ImportError:
        PYPRESENCE_AVAILABLE = False
        print("⚠️  pypresence not installed. Install with: pip install pypresence")


# ============================================================================
# State Management
# ============================================================================

class DiscordRPCState:
    """
    Global state manager for Discord Rich Presence.
    
    Attributes:
        client: pypresence.Presence instance
        connected: Whether currently connected to Discord
        session_start_time: Unix timestamp when session started
        last_update_time: Last time Discord presence was updated
        update_interval: Seconds between Discord updates
        last_save_time: Last time data was saved to disk
    """
    client = None
    connected = False
    session_start_time = None
    last_update_time = 0
    update_interval = 15
    last_save_time = 0
    
    @staticmethod
    def get_data_file():
        """
        Get the path to the persistent data file.
        
        Returns:
            Path: Path to time_tracking.json
        """
        addon_dir = Path(bpy.utils.user_resource('SCRIPTS')) / "addons" / "fawkescord_data"
        addon_dir.mkdir(parents=True, exist_ok=True)
        return addon_dir / "time_tracking.json"
    
    @staticmethod
    def load_persistent_data():
        """
        Load total time from persistent storage.
        
        Returns:
            int: Total seconds tracked, or 0 if file doesn't exist
        """
        try:
            data_file = DiscordRPCState.get_data_file()
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    total_seconds = data.get('total_seconds', 0)
                    was_enabled = data.get('was_enabled', False)
                    
                    if was_enabled:
                        print(f"⚠️  Fawkescord was running when Blender last closed")
                    
                    return total_seconds
        except Exception as e:
            print(f"Error loading persistent data: {e}")
        return 0
    
    @staticmethod
    def save_persistent_data(total_seconds, is_enabled=False):
        """
        Save total time to persistent storage.
        
        Args:
            total_seconds: Total seconds to save
            is_enabled: Whether the addon is currently enabled
        """
        try:
            data_file = DiscordRPCState.get_data_file()
            with open(data_file, 'w') as f:
                json.dump({
                    'total_seconds': total_seconds,
                    'last_save': datetime.now().isoformat(),
                    'was_enabled': is_enabled
                }, f)
        except Exception as e:
            print(f"Error saving persistent data: {e}")

state = DiscordRPCState()


# ============================================================================
# Discord RPC Functions
# ============================================================================

def connect_discord():
    """
    Establish connection to Discord Rich Presence.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    if not PYPRESENCE_AVAILABLE:
        return False
    
    try:
        CLIENT_ID = "1462120962291007570"
        
        state.client = Presence(CLIENT_ID)
        state.client.connect()
        state.connected = True
        state.session_start_time = time.time()
        
        print("✅ Connected to Fawkescord Rich Presence")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Discord: {e}")
        state.connected = False
        return False


def disconnect_discord():
    """
    Disconnect from Discord Rich Presence and clear status.
    """
    if state.client and state.connected:
        try:
            state.client.clear()
            print("🧹 Cleared Discord presence")
            
            state.client.close()
            print("✅ Disconnected from Fawkescord")
        except Exception as e:
            print(f"Error during disconnect: {e}")
    
    state.connected = False
    state.client = None
    state.session_start_time = None


def format_time_detailed(seconds):
    """
    Format seconds into a detailed time string.
    
    Args:
        seconds: Number of seconds to format
        
    Returns:
        str: Formatted string (e.g., "2d 5h 30m")
    """
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or len(parts) == 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts)


def update_discord_presence():
    """
    Update Discord Rich Presence with current Blender state.
    
    Displays current file, mode, session time, and lifetime total.
    """
    if not state.connected or not state.client:
        return
    
    try:
        # Determine what file is being worked on
        blend_file = bpy.data.filepath
        if blend_file:
            file_name = os.path.basename(blend_file)
            if len(file_name) > 30:
                file_name = file_name[:27] + "..."
            details = f"Editing: {file_name}"
        else:
            details = "Working on unsaved file"
        
        # Map Blender modes to readable names
        mode_map = {
            'EDIT_MESH': "Edit Mode",
            'SCULPT': "Sculpting",
            'PAINT_TEXTURE': "Texture Painting",
            'PAINT_WEIGHT': "Weight Painting",
            'PAINT_VERTEX': "Vertex Painting",
            'OBJECT': "Object Mode",
            'POSE': "Pose Mode",
            'EDIT_ARMATURE': "Armature Edit",
        }
        
        current_mode = bpy.context.mode
        state_text = mode_map.get(current_mode, current_mode.replace('_', ' ').title())
        
        # Calculate time statistics
        session_time = int(time.time() - state.session_start_time) if state.session_start_time else 0
        props = bpy.context.scene.fawkescord_props
        total_time = props.total_time_seconds
        
        session_str = format_time_detailed(session_time)
        total_str = format_time_detailed(total_time)
        
        # Get object count for tooltip
        obj_count = len(bpy.data.objects)
        
        # Update Discord presence
        state.client.update(
            details=details,
            state=f"{state_text} | Session: {session_str} | Total: {total_str}",
            start=int(state.session_start_time) if state.session_start_time else None,
            large_image="blender_logo",
            large_text=f"Blender {bpy.app.version_string} | {obj_count} objects",
            small_image="fawkescord",
            small_text="Fawkescord RPC"
        )
        
        state.last_update_time = time.time()
        
    except Exception as e:
        print(f"Error updating Discord presence: {e}")
        state.connected = False


def format_time(seconds):
    """
    Format seconds into a short time string.
    
    Args:
        seconds: Number of seconds to format
        
    Returns:
        str: Formatted string (e.g., "5h 30m" or "30m")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


# ============================================================================
# Blender Properties
# ============================================================================

class FawkescordProperties(bpy.types.PropertyGroup):
    """Property group for Fawkescord addon settings."""
    
    enabled: bpy.props.BoolProperty(
        name="Enable Fawkescord RPC",
        description="Enable Discord Rich Presence",
        default=False,
        update=lambda self, context: toggle_discord_rpc(self, context)
    )
    
    total_time_seconds: bpy.props.IntProperty(
        name="Total Time",
        description="Total time spent in Blender (seconds)",
        default=0
    )
    
    show_file_name: bpy.props.BoolProperty(
        name="Show File Name",
        description="Show current blend file name on Discord",
        default=True
    )
    
    show_mode: bpy.props.BoolProperty(
        name="Show Mode",
        description="Show current editing mode on Discord",
        default=True
    )
    
    auto_connect: bpy.props.BoolProperty(
        name="Auto-Connect on Startup",
        description="Automatically connect to Discord when Blender starts",
        default=False
    )


def toggle_discord_rpc(self, context):
    """
    Callback for enabling/disabling Discord RPC.
    
    Args:
        self: FawkescordProperties instance
        context: Blender context
    """
    if self.enabled:
        if connect_discord():
            if not bpy.app.timers.is_registered(timer_update):
                bpy.app.timers.register(timer_update, persistent=False)
                print("⏱️  Timer started")
    else:
        DiscordRPCState.save_persistent_data(self.total_time_seconds, is_enabled=False)
        disconnect_discord()
        
        if bpy.app.timers.is_registered(timer_update):
            bpy.app.timers.unregister(timer_update)
            print("⏱️  Timer stopped")


# ============================================================================
# Timer Function
# ============================================================================

def timer_update():
    """
    Timer function that runs every second to update time tracking.
    
    Returns:
        float: Interval in seconds until next call (always 1.0)
    """
    try:
        if not hasattr(bpy.context, 'scene'):
            return 1.0
        
        props = bpy.context.scene.fawkescord_props
        
        if props.enabled and state.connected:
            props.total_time_seconds += 1
            
            current_time = time.time()
            
            # Update Discord presence every N seconds
            if current_time - state.last_update_time >= state.update_interval:
                update_discord_presence()
            
            # Save data every 60 seconds
            if current_time - state.last_save_time >= 60:
                DiscordRPCState.save_persistent_data(props.total_time_seconds, is_enabled=True)
                state.last_save_time = current_time
        
        return 1.0
        
    except Exception as e:
        print(f"Timer error: {e}")
        return 1.0


# ============================================================================
# Operators
# ============================================================================

class FAWKESCORD_OT_ResetTotalTime(bpy.types.Operator):
    """Reset the total time counter to zero."""
    bl_idname = "fawkescord.reset_total_time"
    bl_label = "Reset Total Time"
    bl_description = "Reset the total time counter to zero"
    
    def execute(self, context):
        props = context.scene.fawkescord_props
        props.total_time_seconds = 0
        DiscordRPCState.save_persistent_data(0, is_enabled=props.enabled)
        self.report({'INFO'}, "Total time reset")
        return {'FINISHED'}


class FAWKESCORD_OT_ReconnectRPC(bpy.types.Operator):
    """Reconnect to Discord Rich Presence."""
    bl_idname = "fawkescord.reconnect"
    bl_label = "Reconnect"
    bl_description = "Reconnect to Discord Rich Presence"
    
    def execute(self, context):
        disconnect_discord()
        if connect_discord():
            self.report({'INFO'}, "Reconnected to Discord")
        else:
            self.report({'ERROR'}, "Failed to connect to Discord")
        return {'FINISHED'}


class FAWKESCORD_OT_InstallPyPresence(bpy.types.Operator):
    """Install the pypresence library required for Discord RPC."""
    bl_idname = "fawkescord.install_pypresence"
    bl_label = "Install pypresence"
    bl_description = "Install the pypresence library (requires restart)"
    
    def execute(self, context):
        import subprocess
        import sys
        
        try:
            python_exe = sys.executable
            
            # Ensure pip is available
            self.report({'INFO'}, "Ensuring pip is available...")
            try:
                subprocess.check_call([python_exe, "-m", "ensurepip", "--default-pip"])
            except:
                pass
            
            self.report({'INFO'}, "Installing pypresence...")
            
            blender_site_packages = os.path.join(os.path.dirname(python_exe), "..", "lib", "site-packages")
            blender_site_packages = os.path.normpath(blender_site_packages)
            
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", "pypresence", "--target", blender_site_packages],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.report({'INFO'}, "✅ pypresence installed successfully!")
                self.report({'INFO'}, "Please RESTART Blender to use Fawkescord RPC")
            else:
                self.report({'ERROR'}, f"Installation failed: {result.stderr}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
        
        except Exception as e:
            self.report({'ERROR'}, f"Installation failed: {e}")
            print(f"Full error: {e}")
        
        return {'FINISHED'}


# ============================================================================
# UI Panel
# ============================================================================

class FAWKESCORD_PT_MainPanel(bpy.types.Panel):
    """Main panel for Fawkescord Rich Presence controls."""
    bl_label = "Fawkescord RPC"
    bl_idname = "FAWKESCORD_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Fawkescord'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.fawkescord_props
        
        # Header
        box = layout.box()
        row = box.row()
        row.label(text="Fawkescord Rich Presence", icon='COMMUNITY')
        
        # Show installation UI if pypresence not available
        if not PYPRESENCE_AVAILABLE:
            box = layout.box()
            box.label(text="⚠️ pypresence not installed", icon='ERROR')
            box.label(text="Install to enable Discord RPC:")
            box.operator("fawkescord.install_pypresence", icon='IMPORT')
            box.separator()
            box.label(text="Or run as Administrator:")
            box.label(text='pip install pypresence --target "path"')
            return
        
        # Connection status
        box = layout.box()
        if state.connected:
            box.label(text="✅ Connected to Discord", icon='LINKED')
        else:
            box.label(text="❌ Not Connected", icon='UNLINKED')
        
        # Main enable/disable toggle
        layout.separator()
        row = layout.row()
        row.scale_y = 1.5
        row.prop(props, "enabled", text="Enable Rich Presence", toggle=True, 
                icon='PLAY' if not props.enabled else 'PAUSE')
        
        if not props.enabled:
            layout.separator()
            box = layout.box()
            box.label(text="Enable to start tracking", icon='INFO')
            return
        
        # Time tracking display
        layout.separator()
        box = layout.box()
        box.label(text="Time Tracking", icon='TIME')
        
        col = box.column(align=True)
        
        if state.session_start_time:
            session_time = int(time.time() - state.session_start_time)
            session_str = format_time_detailed(session_time)
            col.label(text=f"Session: {session_str}", icon='PREVIEW_RANGE')
        
        total_str = format_time_detailed(props.total_time_seconds)
        col.label(text=f"Lifetime: {total_str}", icon='TRACKING')
        
        box.separator()
        row = box.row()
        row.operator("fawkescord.reset_total_time", text="Reset Lifetime", icon='TRASH')
        
        # Settings
        layout.separator()
        box = layout.box()
        box.label(text="Settings", icon='PREFERENCES')
        col = box.column(align=True)
        col.prop(props, "show_file_name", text="Show File Name")
        col.prop(props, "show_mode", text="Show Edit Mode")
        col.prop(props, "auto_connect", text="Auto-Start")
        
        # Actions
        layout.separator()
        layout.operator("fawkescord.reconnect", text="Reconnect to Discord", icon='FILE_REFRESH')
        
        # Footer
        layout.separator()
        box = layout.box()
        box.scale_y = 0.8
        box.label(text="Time displayed on your Discord profile", icon='INFO')


# ============================================================================
# Registration
# ============================================================================

classes = (
    FawkescordProperties,
    FAWKESCORD_OT_ResetTotalTime,
    FAWKESCORD_OT_ReconnectRPC,
    FAWKESCORD_OT_InstallPyPresence,
    FAWKESCORD_PT_MainPanel,
)


@bpy.app.handlers.persistent
def load_handler(dummy):
    """
    Handler called after Blender loads a file.
    
    Loads persistent time tracking data and auto-connects if enabled.
    """
    if PYPRESENCE_AVAILABLE:
        try:
            total_time = DiscordRPCState.load_persistent_data()
            if hasattr(bpy.context.scene, 'fawkescord_props'):
                bpy.context.scene.fawkescord_props.total_time_seconds = total_time
                print(f"📊 Fawkescord: Loaded lifetime {format_time_detailed(total_time)}")
                
                if bpy.context.scene.fawkescord_props.auto_connect:
                    bpy.context.scene.fawkescord_props.enabled = True
        except:
            pass


@bpy.app.handlers.persistent
def save_handler(dummy):
    """
    Handler called before Blender saves a file.
    
    Saves current time tracking data to persistent storage.
    """
    try:
        if hasattr(bpy.context, 'scene') and hasattr(bpy.context.scene, 'fawkescord_props'):
            props = bpy.context.scene.fawkescord_props
            DiscordRPCState.save_persistent_data(props.total_time_seconds, is_enabled=props.enabled)
            print(f"💾 Fawkescord: Saved {format_time_detailed(props.total_time_seconds)}")
    except Exception as e:
        print(f"Error in save handler: {e}")


def register():
    """Register all Blender classes and handlers."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.fawkescord_props = bpy.props.PointerProperty(type=FawkescordProperties)
    
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)
    
    if save_handler not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(save_handler)
    
    try:
        load_handler(None)
    except:
        pass
    
    print("✅ Fawkescord Rich Presence addon registered")


def unregister():
    """Unregister all Blender classes and handlers."""
    try:
        if hasattr(bpy.context, 'scene') and hasattr(bpy.context.scene, 'fawkescord_props'):
            props = bpy.context.scene.fawkescord_props
            DiscordRPCState.save_persistent_data(props.total_time_seconds, is_enabled=False)
    except:
        pass
    
    disconnect_discord()
    
    if bpy.app.timers.is_registered(timer_update):
        bpy.app.timers.unregister(timer_update)
    
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
    
    if save_handler in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(save_handler)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    if hasattr(bpy.types.Scene, 'fawkescord_props'):
        del bpy.types.Scene.fawkescord_props
    
    print("✅ Fawkescord Rich Presence addon unregistered")


if __name__ == "__main__":
    register()
