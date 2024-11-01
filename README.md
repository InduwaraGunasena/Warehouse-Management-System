# Warehouse Management System

This project is part of my Embedded Systems Project course module in Semester 5.
It combines three key areas of my computer science and engineering curriculum: label segmentation
using a U-Net architecture (Data Science part), a line-following robot (Embedded Systems part), and a
web application for warehouse management (Software Engineering part).

## Table of contents

<!--ts-->

- [Introduction](#Introduction)
- [Backend](#1.Backend)
  - [Starting the Backend](#Starting the Backend)
- [Frontend](#2.Frontend)
  - [Starting the Frontend](#Starting the Frontends)
- [3. Line-Following Robot](#3. Line-Following Robot)
  - [Building the Line-Following Robot](#Building the Line-Following Robot)
  - [Workflow](#Workflow)
- [4. Inventory Analyzer](#4. Inventory Analyzer)
_ [Workflow](#Workflow)
_ [Creating Your Own Dataset](#Creating Your Own Dataset)
_ [Training the Model](#Training the Model)
_ [Running the Inventory Analyzer](#Running the Inventory Analyzer)
<!--te-->

## Introduction

This project is organized into four main components:

1. **Backend** (for the web application)
2. **Frontend** (for the web application)
3. **Line-Following Robot**
4. **Inventory Analyzer**

> ## Prerequisites
>
> Before running this project, ensure the necessary tools are installed:
>
> - **For Backend & Frontend:** Node.js, Git, MongoDB
> - **For Inventory Analyzer:** Python, OpenCV, NumPy, PyTorch
> - **For Line-Following Robot:** Arduino IDE, QTRSensors Library, EEPROMex Library, Encoder Library
>
> After installation, run `npm install` in the backend and frontend directories to install the required npm modules.
> Set up your `.env` files based on the provided `.env.example` files in each directory.

## 1. Backend

The backend, built with Node.js and Express, manages all server-side operations. The backend is using four models:

- **productModel**: for properties of inventory box.
- **tokenModel**: for tokens.
- **userModel**: for user information.
- **warehouseModel**: for rack unit capacities.

Images are stored on Cloudinary; configurations are set in `backend/utils/cloudinaryConfig.js` file. Place your Cloudinary credentials in the backend `.env` file. Local uploads are temporarily stored in `backend/uploads`.

### Starting the Backend

First, Set up a MongoDB server and save add its credentials to `backend/.env` file. Then Start the backend using:

```
npm start
```

## 2. Frontend

The frontend is developed in React, with all required files in `frontend/src`. Users can register, log in, view the warehouse status, inspect inventory details, configure rack units, and manage robot settings. The UI includes an interactive Warehouse Map and a dashboard summarizing warehouse data.

### Starting the Frontend

Ensure the backend is running first, then start the frontend with:

```
npm start
```

## 3. Line-Following Robot

The robot, built with Arduino Mega2560, navigates racks to inspect inventory boxes using an IR sensor array to follow lines. A camera on the robot captures images of each box when an Aruco marker is detected. After that, the robot stops, captures the image, and sends the position and image data to the inventory analyzer.

### Building the Line-Following Robot

Components:

- Arduino Mega2560
- QTR-8RC IR Sensor Array
- HC-06 Bluetooth Module
- L298N Motor Driver
- 2 Gear Motors
- Side Camera for box detection

### Workflow

## 4. Inventory Analyzer

The Inventory Analyzer Python script performs Aruco marker detection, sends commands to the robot, and processes images using a U-Net model for label segmentation. After processing, it sends the data, including positions and segmented images, to the backend.

### Workflow

### Creating Your Own Dataset

### Training the Model

Use `train.py` with your training dataset to train the custom U-Net model. The trained model will be saved as a `.h5` file for label segmentation tasks.

### Running the Inventory Analyzer

Once all libraries are installed, run the analyzer. you can use

```
python main_code.py
```

> [!NOTE]
> Ensure Bluetooth is enabled on your PC, and set up a Wi-Fi webcam for image capture.
