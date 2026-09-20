Computer Science Project 2026-27

Title: The Bohring Engine



Description: The Bohring Engine is an interactive physics engine developed in Python using PyGame, accurately simulating core Newtonian mechanics, collision detection, and response for 2D objects like circles, squares, and rectangles. Users can drag objects in real-time to influence their trajectories, customize initial conditions such as position, velocity, and rotation for any object, or select from preset scenarios like head-on ball collisions or wall bounces. Each simulation run automatically logs initial conditions and key parameters to a MySQL database for analysis and reproducibility, making it an ideal tool for physics education, experimentation, and prototyping game mechanics.


Modules used:  
External - pygame 2.5.2, mysql-connector-python 8.3.0
Standard - math, dataclasses, sys, typing
Project files/User-defined - vector.py, rigidbody.py, physics.py, renderer.py, database.py, config.py, main.py


Software specifications:
Runtime - 
	Language		Python 3.9 or higher
	Recommended		Python 3.11 (fastest CPython)
	pygame version	2.5.2
	mysql-connector	8.3.0
	Package manager	pip (comes with Python)


Database - 
	Engine			MySQL Server 8.0+
	Min. version		MySQL 5.7 (ENUM + FK support) 
	GUI tools		MySQL Workbench, DBeaver, TablePlus 
	Default port		3306


OS & IDE - 
	Windows		10/11
	macOS			12 Monterey+
	Linux			Ubuntu 20.04+ / Debian 11+
	IDE			VS Code + Pylance extension
	Terminal		Any with Python 3.9+



Hardware specifications:
		CPU	         Dual-core 1.5GHz (minimum) / Quad-core 2.0GHz+ (recommended)
		RAM	         512MB (minimum) / 2GB 
		GPU	         Any with hardware-accelerated display
		Display        1280x720 or higher
		Storage        200MB (Python + MySQL + MySQL data)
		Network      None (MySQL runs locally)

Members of the team: Anirudh, Abhimanyu






Go to: https://docs.google.com/document/d/1iEa_WZRIEfzRxlZdo6DI1n1jRxGfkNRyp9Bije1w4Zg/edit?usp=sharing
/\ for adding new presets/scenarios to simulate
