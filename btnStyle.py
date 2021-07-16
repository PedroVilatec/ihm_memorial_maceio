
def btn_style():
	styleBtn = str("""
	QPushButton
	{
	font: 15pt Arial;
	margin: 1px;
	border-color: #0c457e;
	border-style: outset;
	border-radius: 3px;
	border-width: 1px;
	color: white;
	background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2198c0, stop: 1 #0d5ca6);
	}

	QPushButton:pressed
	{
	background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0d5ca6, stop: 1 #2198c0);
	}
""")
	return styleBtn
	
	
def get_QTabBar_style():
	styleStr = str("""
		QTabBar {                                          
			background: None;                         
			color: #ff000000;                              
			font: 12pt Arial;
			min-height: 20px;
			position: west;
										
		}                                                  
		QTabBar::tab {                  
			background: #6574ff;                         
			color: #000000;                              
			border-width: 2px;                             
			border-style: solid;                           
			border-color: #0000ff;                             
			border-bottom-color: #00ffffff;                
			border-top-left-radius: 6px;                   
			border-top-right-radius: 18px;                  
			min-height: 10px;                              
			padding: 2px;                                  
		}                                                  
		QTabBar::tab:selected {
		margin-top: 2px;
			background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2198c0, stop: 1 #0d5ca6);
			border-color:  qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2198c0, stop: 1 #0d5ca6);                             
			border-bottom-color: #0800ff;
		   
		}                                                  
		QTabBar::tab:!selected {                           
			margin-top: 8px;                               
		}                                                  
		QTabBar[colorToggle=true]::tab {                   
		background: #ff0000;                         
		}                                                  
	""")

	return styleStr

def sliderCfg():
	style= ('''
				QSlider::groove:horizontal {
	border: 1px solid;
	background-color: green;
	height: 15px;
	margin: 0px;
}

QSlider::handle:horizontal {
	background-color: green;
	border: 1px solid;
	border-style: outset;
	border-radius: 5px;
	height: 120px;
	width: 40px;
	margin: -30px 0px;
}
''')
	return style
	
def style_player(text):
	
	style = ('''
	QPushButton {
	border-image: url('''+text.replace("\\","/")+''') 3 10 3 10;
	color: #333;
	border: 2px solid #555;
	border-radius: 25px;
	border-style: outset;
	background: qradialgradient(
		cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,
		radius: 1.35, stop: 0 #fff, stop: 1 #888
		);
	padding: 5px;
	}

QPushButton:hover {
	background: qradialgradient(
		cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,
		radius: 1.35, stop: 0 #fff, stop: 1 #bbb
		);
	}

QPushButton:pressed {
	border: 6px solid #555;
	border-radius: 25px;
	border-style:outset;
	background: qradialgradient(
		cx: 0.4, cy: -0.1, fx: 0.4, fy: -0.1,
		radius: 1.35, stop: 0 #fff, stop: 1 #ddd
		);
	}''')


	return style                             
				   
