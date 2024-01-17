# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2023 Ronny Scharf-W. <ronny.scharf08@gmail.com>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

MAIN_STYLE: str = """	
	QWidget {
			font-family: Sans Serif;
			font-size: 12px;
			font-weight: Normal;
		}
		
	QMenu {
		background-color: #191919;
		padding: 5px;
		margin: 0px;
		border: 1px solid #242424;
		border-radius: 0px;
	}
	
	QMenu::item {
		background-color: #191919;
		selection-background-color: #545454;    
		color: #E5E5E5;
		padding-left: 5px;
		padding-right: 15px;
		padding-top: 5px;
		padding-bottom: 5px;
	}
	
	QMenu::item:selected, QMenu::item:pressed {
		background-color: #545454;
		color: #E5E5E5;
	}
	
	QMenu::item:disabled { 
		color: grey;
	}
	
	QMenu::right-arrow, QMenu::right-arrow:selected {
		width: 10px;
		height: 10px;
		margin: 2px;
		padding: 0px;
		image:url(icon:images_dark-light/right_arrow_light.svg);
	}

	QMenu::separator {
		background-color: #242424;
		height: 2px;
	}
	
	QMenu QLineEdit {
		color: #E5E5E5;
		background-color: #191919;
		min-height: 24px;
		max-height: 24px;
		margin: 0px;
		padding: 0px;
		border: 1px solid #545454;
		border-radius: 0px;
		outline: none;
	}
	
	QMenu QLineEdit:focus {
		color: #E5E5E5;
		background-color: #191919;
	}
	
	QMenu QLineEdit:selected {
		color: #E5E5E5;
		background-color: #191919;
	}
	
	QMenu QListView {
		color: #E5E5E5;
		background-color: #191919;
		margin: 0px;
		padding: 0px;
		border: none;
		border-radius: 0px;
		outline: none;
	}
	
	QMenu QListView::item {
		color: #E5E5E5;
		selection-color: #E5E5E5;
		background-color: #191919;
		selection-background-color: #545454;
		min-height: 24px;
		max-height: 24px;
		margin: 0px;
		padding: 0px;
		border: none;
		border-radius: 0px;
		outline: none;
	}
	
	QMenu QListView::item:hover {
		color: #E5E5E5;
		selection-color: #E5E5E5;
		background-color: #545454;
		selection-background-color: #545454;
		margin: 0px;
		padding: 0px;
		border: none;
		border-radius: 0px;
		outline: none;
	}

	QGraphicsView {
		selection-background-color: black;
	}
		
	QScrollArea {
		padding: 0px;
		margin: 0px;
		border: none;
		background-color: #282828;
	}
	
	QTableView {
		color: #E5E5E5;
		selection-color: #E5E5E5;
		background-color: #282828;
		alternate-background-color: #2B2B2B;
		gridline-color: black;
		padding: 0px;
		margin: 0px;
		border: none;
		border-radius: 0px;
		outline: none;
	}
	
	QHeaderView {
		font-family: Sans Serif;
		font-size: 12px;
		font-weight: Normal;
	}

	QHeaderView::section:horizontal {
		color: #E5E5E5;
		background-color: #3D3D3D;
		margin: 0px;
		padding: 0px;
		border-top: none;
		border-bottom: 1px solid black;
		border-left: none;
		border-right: 1px solid black;
	}

	QTableView::item {
		border: none;
		margin: 0px;
		padding: 0px;
	}

	QTableView::item:selected {
		background-color: #545454;
	}

	QTableView::item:hover {
		border: none;
	}

	QTableView::item:focus {
		border: none;
	}

	QSpinBox {
		color: #E5E5E5;
		background-color: #545454;
		selection-background-color: #191919;
		padding-left: 1px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 1px;
		margin: 0px;
		border: none;
	}
	
	QSpinBox:focus {
		color: #E5E5E5;
		background-color: #545454;
	}
	
	QSpinBox:selected {
		color: #E5E5E5;
		background-color: #545454;
	}
	
	QSpinBox::up-arrow {
		width: 12px; 
		height: 12px;
		background-color: transparent;
		image: url(icon:images_dark-light/up_arrow_light.svg);
		/*image: url(qss:images_dark-light/down_arrow_light.svg);*/
	}
	
	QSpinBox::up-button{
		background-color: transparent;
	}
	
	QSpinBox::down-arrow {
		width: 12px; 
		height: 12px;
		background-color: transparent;           
		image: url(icon:images_dark-light/down_arrow_light.svg);
		/*image: url(qss:images_dark-light/down_arrow_light.svg);*/
	}
	
	QSpinBox::down-button{
		background-color: transparent;
	}
	
	QComboBox {
		color: #E5E5E5;
		background-color: #545454;
		border-radius: 0px;
		padding-left: 3px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 1px;
		margin: 0px;
		border: none;
	}
	
	QComboBox:focus {
		color: #E5E5E5;
		background-color: #545454;
	}
	
	QComboBox:selected {
		color: #E5E5E5;
		background-color: #545454;
	}
	
	QComboBox::drop-down {
		background-color: transparent;
		subcontrol-origin: border;
		subcontrol-position: top right;
		padding-left: 0px;
		padding-right: 8px;
		padding-top: 0px;
		padding-bottom: 0px;
		border-radius: 0px;
	}
	
	QComboBox::down-arrow {
		width: 10px; 
		height: 10px;
		image: url(icon:images_dark-light/down_arrow_light.svg);
		/*image: url(qss:images_dark-light/down_arrow_light.svg);*/
	}
	
	QListView{
		border: none;
	}
	
	QAbstractItemView {
		color: #E5E5E5;
		selection-color: #E5E5E5;
		background-color: #282828;
		selection-background-color: #545454;
		margin: 0px;
		padding: 0px;
		border: none;
		border-radius: 0px;
		outline: none;
	}
	
	QLineEdit {
		color: #E5E5E5;
		background-color: #545454;
		selection-background-color: #191919;
		padding-left: 1px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 1px;
		margin: 0px;
		border: none;
	}
	
	QLineEdit:focus {
		color: #E5E5E5;
		background-color: #545454;
	}
	
	QLineEdit:selected {
		color: #E5E5E5;
		background-color: #545454;
	}
"""

NODE_STYLE: str = """
	QWidget {
		font-family: Sans Serif;
		font-size: 12px;
		font-weight: Normal;
		background-color: #303030;
	}
	
	QLabel {
		color: #E5E5E5;
		background-color: #545454;
		min-height: 24px;
		max-height: 24px;
		margin-left: 0px;
		margin-right: 0px;
		margin-top: 0px;
		margin-bottom: 0px;
		padding-left: 3px;
		padding-right: 3px;
		padding-top: 0px;
		padding-bottom: 0px;
		border-top-left-radius: 0px; /*5px;*/
		border-bottom-left-radius: 0px; /*5px;*/
		border-top-right-radius: 0px;
		border-bottom-right-radius: 0px;
		border: 0px;
	}
	
	QLineEdit {
		color: #E5E5E5;
		background-color: #545454;
		selection-background-color: #191919;
		min-height: 24px;
		max-height: 24px;
		margin-left: 0px;
		margin-right: 0px;
		margin-top: 0px;
		margin-bottom: 0px;
		padding-left: 3px;
		padding-right: 3px;
		padding-top: 0px;
		padding-bottom: 0px;
		border-top-left-radius: 0px;
		border-bottom-left-radius: 0px;
		border-top-right-radius: 0px; /*5px;*/
		border-bottom-right-radius: 0px; /*5px;*/
		border: 0px;
	}
	
	QComboBox {
		color: #E5E5E5;
		background-color: #282828;
		border-radius:  0px; /*5px;*/
		min-width: 5px;
		min-height: 24px;
		max-height: 24px;
		padding-left: 10px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 0px;
		margin: 0px;
		border: 1px solid #242424;
	}
	
	QComboBox::drop-down {
		background-color: #545454;
		subcontrol-origin: border;
		subcontrol-position: top right;
		width: 20px;
		border-top-right-radius: 0px; /*5px;*/
		border-bottom-right-radius: 0px; /*5px;*/
		border-top-left-radius: 0px;
		border-bottom-left-radius: 0px;
	}
	
	QComboBox::down-arrow {
		width: 10px; 
		height: 10px;
		image: url(icon:images_dark-light/down_arrow_light.svg);
		/*image: url(qss:images_dark-light/down_arrow_light.svg);*/
	}
	
	QListView{
		border: none;
	}
	
	QAbstractItemView {
		color: #E5E5E5;
		selection-color: #E5E5E5;
		background-color: #282828;
		selection-background-color: #191919;
		min-width: 20px;
		min-height: 24px;
		padding-left: 5px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 0px;
		margin: 0px;
		border: 1px solid #242424;
		border-radius: 0px;
		outline: none;
	}
	
	QCheckBox{
		color: #E5E5E5;
		background-color: #545454;
		min-width: 5px;
		min-height: 24px;
		max-height: 24px;
		margin-left: 0px;
		margin-right: 0px;
		margin-top: 0px;
		margin-bottom: 0px;
		padding-left: 10px;
		padding-right: 10px;
		padding-top: 0px;
		padding-bottom: 0px;
	}
"""
