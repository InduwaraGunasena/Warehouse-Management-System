# Warehouse Management System

This project is part of my Embedded Systems Project course module in Semester 5.
It combines three key areas of my computer science and engineering curriculum: label segmentation
using a U-Net architecture (Data Science part), a line-following robot (Embedded Systems part), and a
web application for warehouse management (Software Engineering part).

You can watch [this video](https://pages.github.com/) to know how this works .

## Table of contents

<!--ts-->

- [Introduction](#Introduction)
- [Backend](#1-Backend)
  - [Starting the Backend](#Starting-the-Backend)
- [Frontend](#2-Frontend)
  - [Starting the Frontend](#Starting-the-Frontends)
- [Line-Following Robot](#3-Line-Following-Robot)
  - [Building the Line-Following Robot](#Building-the-Line-Following-Robot)
  - [Workflow](#Workflow)
- [Inventory Analyzer](#4-Inventory-Analyzer)
  - [Workflow](#Workflow)
  - [Creating Your Own Dataset](#Creating-Your-Own-Dataset)
  - [Training the Model](#Training-the-Model)
  - [Running the Inventory Analyzer](#Running-the-Inventory-Analyzer)
  <!--te-->

## Introduction

This project is organized into four main components:

1. **Backend** (for the web application)
2. **Frontend** (for the web application)
3. **Line-Following Robot**
4. **Inventory Analyzer**

The backend and frontend is related with the Warehouse Management System(WMS). The line following robot consist with an IP-camera
to capture images of inventory boxes. The inventory analyzer runs on my laptop. The following image describes copnnections between those entitites.

<p align="center">
<img src="/images/image1.png" alt="The Block diagram of main 4 entities" width="500"/>
<br><em><sub>The Block diagram of main 4 entities</sub></em>
</p>

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

Images are stored on Cloudinary; configurations are set in `backend/utils/cloudinaryConfig.js` file. Remember to place your Cloudinary credentials in the backend `.env` file. Local uploads are temporarily stored in `backend/uploads`.

### Starting the Backend

First, Set up a MongoDB server and remember to save its URI into `backend/.env` file. Then Start the backend using:

```
npm start
```

## 2. Frontend

The frontend is developed in React, with all required files in `frontend/src`.

After run the frontend user will be move into Home page. Users can Login or sigup from there.

<p align="center">
<img src="/images/image2.gif" alt="Homepage" width="500"/>
</p>

After login, user can have the access to the WMS and move into dashboard. This includes an interactive Warehouse Map and a dashboard summarizing warehouse data.

<p align="center">
<img src="/images/image3.png" alt="Dashboard" width="500"/>
</p>

Users can view the labels and the position of any inventory box from the **Warehouse Map** section.

<p align="center">
<img src="/images/image4.gif" alt="Warehouse Map" width="500"/>
</p>

Users can configure a rack in **Warehouse** section in menu bar at the right side. In this page, you can configure
the number of units in a single rack.

<p align="center">
<img src="/images/image5.gif" alt="Warehouse" width="500"/>
</p>

> [!NOTE]
> Here users can configure pnly upto 5 units and I considered only a single rack having one shelf.(That was for my ease😁)

The neccesory setting and details can be seen from the **Robot** section from the menu bar(didn't completed it yet 😢)

Users can view their account and edit their user information using **Account** section in the menu bar. Also report any bug via **Report Bug** section.

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

The following image shows the block diagram of how these components wired.

<p align="center">
<img src="/images/image6.gif" alt="Block diagram of the robot" width="500"/>
</p>

### Workflow

The following diagram shows the workflow of the robot process as a flow chart.

<p align="center">
<img src="/images/image7.png" alt="Workflow of the robot" width="500"/>
</p>

## 4. Inventory Analyzer

The Inventory Analyzer Python script performs Aruco marker detection, sends commands to the robot, and processes images using a U-Net model for label segmentation. After processing, it sends the data, including positions and segmented images, to the backend.

### Workflow

I use two threads for read receiving messages and detect Aruco markers.
this image shows flow chart of this process.

<p align="center">
<img src="/images/image8.png" alt="Workflow of the inventory analyzer" width="500"/>
</p>

### Creating Your Own Dataset

First you need to collect some images (at least 100 for reliable results) and annotate them using tools like ImgLab.
Use `label_segmentation/dataCreator` jupyter notebook codes to prepare the dataset for training.
In there, it has some codes to verify annotations manually so it might heplful to ensure dataset accuracy.

### Training the Model

Use `train.py` with your training dataset to train the custom U-Net model. The trained model will be saved as a `.h5` file for label segmentation tasks.

### Running the Inventory Analyzer

Once all libraries are installed, run the analyzer. you can use

```
python main_code.py
```

> [!NOTE]
> Ensure Bluetooth is enabled on your PC, and set up a Wi-Fi webcam for image capture.

> ## References
>
> You can refer these things and might be helpful to change things.
>
> - I followed the tutorial to build this WMS web application.
> - If you don't know how to segment using U-Net, You can learn from [this video series](https://www.youtube.com/watch?v=Xh4r4akBibM&list=PL_Nji0JOuXg1OCpsGtHs6VyF-K6acaVgA&pp=iAQB).
> - I implemented the U-Net architecture using [this](https://github.com/pagi-ai/U-Net) github repo.
