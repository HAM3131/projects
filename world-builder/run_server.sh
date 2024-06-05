#!/bin/bash

# Build User Interface
cd map
npm install
npm run build
rm -rf ../public/map/*
cp -r build/* ../public/map
cd ..

# Build Admin Interface
cd map-admin
npm install
npm run build
rm -rf ../public/map-admin/*
cp -r build/* ../public/map-admin
cd ..

# Start the Server
npm run dev
