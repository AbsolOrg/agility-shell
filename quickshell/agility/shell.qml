import QtQuick
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

ShellRoot {
    IpcHandler {
        target: "suits"
        function reload() {
            Theme.reloadSettings()
        }
    }

    Variants {
        model: Quickshell.screens
        PanelWindow {
            id: desktopWindow
            property var modelData
            screen: modelData

            WlrLayershell.layer: WlrLayer.Bottom
            WlrLayershell.namespace: "quickshell:agility-desktop-widgets"
            WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

            anchors {
                top: true
                bottom: true
                left: true
                right: true
            }
            color: "transparent"

            mask: Region {
                Region { item: clockWidget }
                Region { item: sysinfoWidget }
                Region { item: calendarWidget }
                Region { item: mediaWidget }
                Region { item: weatherWidget }
                Region { item: posterWidget }
                Region { item: batteryWidget }
                Region { item: volumeWidget }
                Region { item: networkWidget }
                Region { item: notesWidget }
                Region { item: todoWidget }
                Region { item: timerWidget }
                Region { item: thermalWidget }
                Region { item: quoteWidget }
                Region { item: clipboardWidget }
                Region { item: cryptoWidget }
                Region { item: worldclockWidget }
                Region { item: gitWidget }
                Region { item: resourcewheelWidget }
                Region { item: visualizerWidget }
                Region { item: habitsWidget }
                Region { item: pingWidget }
                Region { item: storagemapWidget }
                Region { item: calcWidget }
            }

            Connections {
                target: Theme
                function onSettingsUpdated() {
                    if (!Theme.isSwitching) return
                    Theme.applyWidgetConfig(clockWidget, "clock")
                    Theme.applyWidgetConfig(sysinfoWidget, "sysinfo")
                    Theme.applyWidgetConfig(calendarWidget, "calendar")
                    Theme.applyWidgetConfig(mediaWidget, "media")
                    Theme.applyWidgetConfig(weatherWidget, "weather")
                    Theme.applyWidgetConfig(posterWidget, "poster")
                    Theme.applyWidgetConfig(batteryWidget, "battery")
                    Theme.applyWidgetConfig(volumeWidget, "quickcontrols")
                    Theme.applyWidgetConfig(networkWidget, "network")
                    Theme.applyWidgetConfig(notesWidget, "notes")
                    Theme.applyWidgetConfig(todoWidget, "todo")
                    Theme.applyWidgetConfig(timerWidget, "timer")
                    Theme.applyWidgetConfig(thermalWidget, "thermal")
                    Theme.applyWidgetConfig(quoteWidget, "quote")
                    Theme.applyWidgetConfig(clipboardWidget, "clipboard")
                    Theme.applyWidgetConfig(cryptoWidget, "crypto")
                    Theme.applyWidgetConfig(worldclockWidget, "worldclock")
                    Theme.applyWidgetConfig(gitWidget, "git")
                    Theme.applyWidgetConfig(resourcewheelWidget, "resourcewheel")
                    Theme.applyWidgetConfig(visualizerWidget, "visualizer")
                    Theme.applyWidgetConfig(habitsWidget, "habits")
                    Theme.applyWidgetConfig(pingWidget, "ping")
                    Theme.applyWidgetConfig(storagemapWidget, "storagemap")
                    Theme.applyWidgetConfig(calcWidget, "calc")
                }
            }

            Item {
                id: widgetsLayer
                anchors.fill: parent

                Clock {
                    id: clockWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("clock") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("clock") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                SystemInfo {
                    id: sysinfoWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("sysinfo") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("sysinfo") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                CalendarWidget {
                    id: calendarWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("calendar") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("calendar") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                MediaWidget {
                    id: mediaWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("media") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("media") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                WeatherWidget {
                    id: weatherWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("weather") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("weather") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                PosterWidget {
                    id: posterWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("poster") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("poster") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                BatteryWidget {
                    id: batteryWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("battery") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("battery") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                VolumeBrightnessWidget {
                    id: volumeWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("quickcontrols") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("quickcontrols") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                NetworkWidget {
                    id: networkWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("network") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("network") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                NotesWidget {
                    id: notesWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("notes") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("notes") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                TodoWidget {
                    id: todoWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("todo") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("todo") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                TimerWidget {
                    id: timerWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("timer") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("timer") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                ThermalWidget {
                    id: thermalWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("thermal") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("thermal") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                QuoteWidget {
                    id: quoteWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("quote") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("quote") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                ClipboardWidget {
                    id: clipboardWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("clipboard") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("clipboard") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                CryptoWidget {
                    id: cryptoWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("crypto") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("crypto") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                WorldClockWidget {
                    id: worldclockWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("worldclock") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("worldclock") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                GitDashboardWidget {
                    id: gitWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("git") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("git") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                ResourceWheelWidget {
                    id: resourcewheelWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("resourcewheel") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("resourcewheel") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                VisualizerWidget {
                    id: visualizerWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("visualizer") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("visualizer") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                HabitsWidget {
                    id: habitsWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("habits") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("habits") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                PingWidget {
                    id: pingWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("ping") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("ping") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                StorageMapWidget {
                    id: storagemapWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("storagemap") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("storagemap") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }

                CalcWidget {
                    id: calcWidget
                    visible: opacity > 0.001
                    opacity: Theme.isWidgetVisible("calc") ? 1.0 : 0.0
                    scale: Theme.isWidgetVisible("calc") ? 1.0 : 0.88
                    Behavior on x { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on y { enabled: Theme.isSwitching; NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
                    screenWidth: desktopWindow.width
                    screenHeight: desktopWindow.height
                }
            }
        }
    }
}
