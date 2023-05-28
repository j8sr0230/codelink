APP_STYLE: str = """

QScrollArea {
	padding: 0px;
	margin: 0px;
	border: none;
}

QSpinBox {
	color: #E5E5E5;
	background-color: #545454;
	selection-background-color: black;
	padding-left: 1px;
	padding-right: 0px;
	padding-top: 0px;
	padding-bottom: 1px;
	margin: 0px;
	border: none;
}
QTableView QSpinBox:focus {
	color: #E5E5E5;
	background-color: #545454;
}
QTableView QSpinBox:selected {
	color: #E5E5E5;
	background-color: #545454;
}
QTableView QSpinBox::up-arrow {
	width: 12px; 
	height: 12px;
	background-color: transparent;
	image: url(icon:images_dark-light/up_arrow_light.svg);
	/*image: url(qss:images_dark-light/down_arrow_light.svg);*/
}
QTableView QSpinBox::up-button{
	background-color: transparent;
}
QTableView QSpinBox::down-arrow {
	width: 12px; 
	height: 12px;
	background-color: transparent;           
	image: url(icon:images_dark-light/down_arrow_light.svg);
	/*image: url(qss:images_dark-light/down_arrow_light.svg);*/
}
QTableView QSpinBox::down-button{
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
	selection-background-color: black;
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