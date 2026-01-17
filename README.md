# Fawkescord Rich Presence

A Blender addon that displays your Blender activity on Discord with accurate time tracking.

![Blender Version](https://img.shields.io/badge/Blender-4.0%2B-orange)
![Version](https://img.shields.io/badge/version-1.3.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Discord Rich Presence integration - Display your Blender activity on your Discord profile
- Session Tracking - Track time for your current Blender session
- Lifetime Statistics - Persistent tracking of total time spent in Blender
- File Information - Show the current blend file you're working on
- Mode Detection - Displays your current editing mode (Object, Edit, Sculpt, etc.)
- Auto-Connect - Optional automatic connection when Blender starts
- Persistent Data - Time tracking data survives Blender restarts
- Clean Disconnection - Properly clears Discord status when disabled

## Screenshots
![Discord Profile](https://i.ibb.co/mCV9qyXL/Fawkescord-Tracker.png)
Your Discord profile will display:
- **Line 1**: Current file name or "Working on unsaved file"
- **Line 2**: Current mode, session time, and lifetime total
- **Tooltip**: Blender version and object count

Example Discord status:
```
Editing: my_project.blend
Object Mode | Session: 1h 23m | Total: 45h 12m
```

## Installation

### Method 1: Automatic Installation (Recommended)

1. Download the addon file (`fawkescord_rpc.py`)
2. Open Blender
3. Go to `Edit` → `Preferences` → `Add-ons`
4. Click `Install...` and select the downloaded file
5. Enable the addon by checking the box next to "Fawkescord Rich Presence"
6. The addon will prompt you to install `pypresence` - click the install button
7. **Restart Blender** after installation completes

### Method 2: Manual Installation

1. Install the `pypresence` library:
   ```bash
   # On Windows (run as Administrator)
   "C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin\python.exe" -m pip install pypresence
   
   # On macOS
   /Applications/Blender.app/Contents/Resources/4.0/python/bin/python3.10 -m pip install pypresence
   
   # On Linux
   /path/to/blender/4.0/python/bin/python3.10 -m pip install pypresence
   ```

2. Follow steps 1-5 from Method 1

## Usage

### Getting Started

1. Open Blender and find the Fawkescord panel in the 3D Viewport sidebar (press `N` to toggle)
2. Navigate to the `Fawkescord` tab
3. Click `Enable Rich Presence` to start tracking
4. Your Discord status will update automatically

### Features

#### Time Tracking
- **Session Time**: Resets each time you start Blender
- **Lifetime Time**: Cumulative time across all sessions
- **Auto-Save**: Data is saved every 60 seconds and when you close Blender

#### Settings
- **Show File Name**: Toggle file name display on Discord
- **Show Edit Mode**: Toggle current mode display
- **Auto-Start**: Automatically connect when Blender starts

#### Controls
- **Reset Lifetime**: Clear your total time counter
- **Reconnect**: Manually reconnect to Discord if connection is lost

## Configuration

All settings are accessible from the addon panel in Blender:

| Setting | Description | Default |
|---------|-------------|---------|
| Enable Rich Presence | Turn Discord integration on/off | Off |
| Show File Name | Display current blend file name | On |
| Show Edit Mode | Display current editing mode | On |
| Auto-Start | Auto-connect on Blender startup | Off |

## File Structure

```
fawkescord_data/
└── time_tracking.json    # Persistent time data
```

The addon stores time tracking data in your Blender scripts directory:
- **Windows**: `%APPDATA%\Blender Foundation\Blender\4.0\scripts\addons\fawkescord_data\`
- **macOS**: `~/Library/Application Support/Blender/4.0/scripts/addons/fawkescord_data/`
- **Linux**: `~/.config/blender/4.0/scripts/addons/fawkescord_data/`

## Troubleshooting

### "pypresence not installed" error
- Use the built-in installer button in the addon panel
- Alternatively, manually install using the commands in the installation section
- Make sure to restart Blender after installation

### Discord status not showing
- Ensure Discord is running
- Check that you're not appearing as "Invisible" in Discord
- Try using the "Reconnect" button in the addon panel
- Verify that Discord Rich Presence is enabled in Discord Settings → Activity Settings → Activity Privacy

### Time tracking seems incorrect
- The addon only tracks time when enabled and Blender is running
- Use "Reset Lifetime" to start fresh if needed
- Check the data file hasn't been manually modified

### Connection issues
- Restart Discord
- Restart Blender
- Try disabling and re-enabling the addon
- Check if Discord's RPC feature is working with other applications

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install pypresence`
3. Make your changes
4. Test in Blender
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use clear, descriptive variable names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with [pypresence](https://github.com/qwertyquerty/pypresence) by qwertyquerty
- Inspired by the Blender community's love for sharing their work
- Discord Rich Presence API by Discord

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/fawkescord/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fawkescord/discussions)

## Roadmap

- Custom status messages
- More detailed activity tracking
- Theme customization
- Statistics dashboard
- Export time reports
- Multi-language support

## Changelog

### v1.3.1 (Current)
- Fixed time tracking continuing when Blender is closed
- Added proper Discord presence clearing on disconnect
- Improved session state management
- Added comprehensive error handling
- Better documentation and code comments

### v1.3.0
- Initial public release
- Basic Discord Rich Presence integration
- Session and lifetime time tracking
- Auto-connect feature

---

Made by Fawkes
