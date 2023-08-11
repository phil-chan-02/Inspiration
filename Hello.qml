//Copyright (c) 2018 Ultimaker B.V.
//This example is released under the terms of the AGPLv3 or higher.

import UM 1.5 as UM //This allows you to use all of Uranium's built-in QML items.
import Cura 1.0 as Cura
import QtQuick 2.7 //This allows you to use QtQuick's built-in QML items.
import QtQuick.Controls 2.3
import QtQuick.Window 2.2
import QtQuick.Layouts 1.2

Window{
    id: inspirationBase
    title: "AIGC Test"
    modality: Qt.NonModal
    // Qt.ApplicationModal
    width: 1200 * screenScaleFactor
    height: 640 * screenScaleFactor
    minimumWidth: 800 * screenScaleFactor
    minimumHeight: 400 * screenScaleFactor

    Item{
        id: image_area
        width: 3/5 * parent.width
        height: 4/5 * parent.height
        
        anchors{
            top: parent.top
            left: parent.left
        }

        Image{
            id: image_items
            width: 300 * screenScaleFactor
            height: 300 * screenScaleFactor
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: image_area

            Connections{
                target: manager
                onCurrentImageDeleted: {
                    image_items.source = manager.deleteIconPath
                }
                onCurrentImageChanged: {
                    image_items.source = "./images/" + manager.currentImageId
                }
            }
        
            Drag.imageSource: image_items.source
            Drag.active: drag_area.drag.active
            Drag.dragType: Drag.Automatic
            Drag.supportedActions: Qt.CopyAction
            Drag.mimeData: {
                "text/uri-list": qsTr("file:///" + manager.getQtCurrentDir + "/images/" + manager.currentImageId),
            }

            MouseArea{
                id: drag_area
                anchors.fill: parent
                drag.target: parent
            }
        }

        
    }

    Item{
        id: console_area
        height: parent.height
        
        anchors{
            top: parent.top
            left: image_area.right
            right: parent.right
        }

        Rectangle{
            border.color: UM.Theme.getColor("lining")
			border.width: UM.Theme.getSize("default_lining").width
            color: "transparent"
            anchors.fill: parent

            GridLayout{
                id: console_grid
                columns: 2
                height: 3/5 * parent.height
                anchors{
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    margins: 10
                }

                Repeater{
                    model: ['图片描述', '宽度', '高度']
                    Text{
                        Layout.column: 0
                        Layout.row: index
                        text: modelData + ": "
                    }
                }
                Repeater{
                    model: ['Prompt', 'Width', 'Height']
                    Rectangle {
                        Layout.column: 1
                        Layout.row: index
                        width: 100
                        height: 24
                        color: "lightgrey"
                        border.color: "grey"

                        TextInput {
                            id: console_text
                            anchors.fill: parent
                            anchors.margins: 2
                            font.pointSize: 15
                            focus: true
                            onEditingFinished: {
                                manager.setSubmitData(modelData, console_text.text)
                            }
                        }
                    }
                }
            }

            Text{
                id: console_text
                text: "支持的宽度×高度：512x512、640x360、360x640、1024x1024、1280x720、720x1280，千万不要输错，会报错"
                clip: true
                width: console_grid.width
                wrapMode: Text.WrapAnywhere

                height: 1/5 * parent.height
                anchors{
                    top: console_grid.bottom
                    left: console_grid.left
                    right: console_grid.right
                }
            }

            Button{
                id: test_button
                text: "删除图片"
                anchors{
                    top: console_text.bottom
                    right: test_button.left
                    margins: 10
                }
                    
                onClicked: {
                    manager.popDeleteBox()
                }
            }

            Button{
                id: result_button
                text: "获取图片"

                anchors{
                    top: console_text.bottom
                    right: parent.right
                    margins: 10
                }
                onClicked: {
                    manager.getImageViaApi()
                }

            }
        } 
    }

    Item{
        id: candidate_box
        width: image_area.width

        anchors{
            top: image_area.bottom
            bottom: parent.bottom
            left: parent.left
        }
        Rectangle{
            border.color: UM.Theme.getColor("lining")
			border.width: UM.Theme.getSize("default_lining").width
            color: "transparent"
            anchors.fill: parent
            Label{
                id: box_label
                width: 1/6 * parent.width
                height: 1/4 * parent.height 
                text: "Box"

                anchors{
                    left: parent.left
                    top: parent.top
                }
            }
            ScrollView{
                id: bow_scroll
                clip: true
                ScrollBar.vertical.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.interactive: false
                anchors{
                    left: parent.left
                    top: box_label.bottom
                    bottom: parent.bottom
                    right: parent.right
                }
                Row{
                    id: box_row
                    width: parent.width
                    spacing: 20

                    anchors{
                        left: parent.left
                        top: box_label.bottom
                        bottom: parent.bottom
                    }
                
                    Repeater{
                        model: manager.imagesList
                        Image{
                            cache: false
                            width: 100 * screenScaleFactor
                            height: 100 * screenScaleFactor
                            fillMode: Image.PreserveAspectFit
                            source: "./images/" + modelData
                            MouseArea{
                                id: mouse_area
                                anchors.fill: parent
                                onClicked: {
                                    manager.setCurrentImageId(modelData)
                                }
                            }    
                        }

                    }
                }
            }           
        }
    }
}
