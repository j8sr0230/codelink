MAIN_STYLE: str = """
	QScrollArea {
		padding: 0px;
		margin: 0px;
		border: none;
		background-color: transparent;
	}
	
	QTableView {
		font-family: Sans Serif;
		font-size: 12px;
		font-weight: Normal;
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
		selection-background-color: black;
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

NODE_STYLE: str = """
	QWidget {
		font-family: Sans Serif;
		font-size: 12px;
		font-weight: Normal;
		background-color: transparent;
	}
	
	QLabel {
		color: #E5E5E5;
		background-color: #545454;
		min-height: 24px;
		max-height: 24px;
		margin-left: 0px;
		margin-right: 1px;
		margin-top: 0px;
		margin-bottom: 0px;
		padding-left: 10px;
		padding-right: 10px;
		padding-top: 0px;
		padding-bottom: 0px;
		border-top-left-radius: 5px;
		border-bottom-left-radius: 5px;
		border-top-right-radius: 0px;
		border-bottom-right-radius: 0px;
		border: 0px;
	}
	
	QLineEdit {
		color: #E5E5E5;
		background-color: #545454;
		selection-background-color: black;
		min-width: 5px;
		min-height: 24px;
		max-height: 24px;
		margin-left: 1px;
		margin-right: 0px;
		margin-top: 0px;
		margin-bottom: 0px;
		padding-left: 10px;
		padding-right: 10px;
		padding-top: 0px;
		padding-bottom: 0px;
		border-top-left-radius: 0px;
		border-bottom-left-radius: 0px;
		border-top-right-radius: 5px;
		border-bottom-right-radius: 5px;
		border: 0px;
	}
	
	QComboBox {
		color: #E5E5E5;
		background-color: #282828;
		border-radius: 5px;
		min-width: 5px;
		min-height: 24px;
		max-height: 24px;
		padding-left: 10px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 0px;
		margin: 0px;
		border: 0px;
	}
	
	QComboBox::drop-down {
		background-color: #545454;
		subcontrol-origin: border;
		subcontrol-position: top right;
		width: 20px;
		border-top-right-radius: 5px;
		border-bottom-right-radius: 5px;
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
		selection-background-color: black;
		min-width: 20px;
		min-height: 24px;
		padding-left: 5px;
		padding-right: 0px;
		padding-top: 0px;
		padding-bottom: 0px;
		margin: 0px;
		border: 0px;
		border-radius: 0px;
	}
"""