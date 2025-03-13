# Modern Music Player

[![codecov](https://codecov.io/gh/harley029/PyQt_Advanced_Music_Player/branch/main/graph/badge.svg?token=6RNGBY6IXK)](https://codecov.io/gh/harley029/PyQt_Advanced_Music_Player)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/26102897f0694ae4b45d9106dc270160)](https://app.codacy.com/gh/harley029/PyQt_Advanced_Music_Player/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=harley029_PyQt_Advanced_Music_Player&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=harley029_PyQt_Advanced_Music_Player)
[![Build Status](https://github.com/harley029/PyQt_Advanced_Music_Player/actions/workflows/ci.yml/badge.svg)](https://github.com/harley029/PyQt_Advanced_Music_Player/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![Player](utils/screenshots/qtbeets2.png)

## 1. General Analysis of the Project as a Whole

The project is a desktop music player application built using PyQt5. It is organized into multiple modules that handle the user interface, database operations, event handling, and playback functionality. The architecture follows a modular design with dependency injection, which facilitates testing and enhances flexibility. Key design patterns implemented in the project include the Factory, Command, Strategy, and Dependency Injection patterns.

### Try out the last build (for Mac OS only)

- Download the artifact from [the latest Build macOS App](https://github.com/harley029/PyQt_Advanced_Music_Player/actions).
- Unpack the package into the separate folder
- Open Terminal in that folder
- Run the command to bypasses the Gatekeeper: "xattr -d com.apple.quarantine qtbeets-1.4.app"
- Enjoy the fully operable application qtbeets-1.4.app

## 2. General Analysis of Each Module

### 2.1. Main UI (QtBeets.py)

Initializes core components, sets up the main window, and manages UI events. It uses classes such as WindowManager, UIUpdater, and EventHandler to delegate functionality.

### 2.2. Database Module (db_manager.py & db_utils.py)

Implements SQLite database operations including connection management, query execution, table creation, and data manipulation. It also includes utility functions for validating table names.

### 2.3. Controllers

#### 2.3.1. MusicPlayerController

Wraps the QMediaPlayer to manage playback functions such as play, pause, stop, and volume control.

#### 2.3.2. UIUpdater

Synchronizes the music player’s state with the UI (e.g., slider position, time labels, and song metadata).

#### 2.3.3. EventHandler

Coordinates user interactions by delegating tasks to specialized handlers like PlaybackHandler, NavigationHandler, and UIEventHandler.

#### 2.3.4. Utility Modules

Provide shared functionality including message management (MessageManager), UI component access (UIProvider), and list management (ListManager).

#### 2.3.5. Command & Context Menu Modules

Implement the Command pattern to encapsulate user actions, allowing for decoupled and easily extendable command execution within the UI.

## 3. Detailed Analysis from the Perspective of SOLID Principles

### Single Responsibility Principle (SRP)

Each class is designed to handle a specific responsibility. For example, UIUpdater solely updates UI elements while MusicPlayerController handles playback.

### Open/Closed Principle (OCP)

The application is extensible via dependency injection and the use of interfaces. This allows new features or modifications to be added with minimal changes to the existing codebase.

### Liskov Substitution Principle (LSP)

Interfaces such as IMusicPlayerController and IUIProvider ensure that different implementations can be substituted without affecting the overall functionality of the application.

### Interface Segregation Principle (ISP)

The interfaces are fine-grained and focused on specific functionalities, ensuring that classes only need to implement the methods that are relevant to their operations.

### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions rather than concrete implementations. The use of configuration objects (e.g., EventHandlerConfig) and dependency injection throughout the project exemplify this principle.

## 4. Detailed Analysis from the Perspective of the DRY Principle

### Avoiding Repetition

Common functionality is abstracted into utility classes such as UIProvider, ListManager, and MessageManager. This centralization reduces code duplication and simplifies maintenance.

### Shared Methods

Methods for common tasks (e.g., list validation, message display, widget access) are implemented once and reused across multiple modules, ensuring consistency and reducing the likelihood of errors.

## 5. Detailed Analysis from the Perspective of Structural Programming Patterns

### Factory Pattern

The AppFactory is used to create and wire up all dependencies, centralizing the instantiation logic and making the application setup more manageable.

### Command Pattern

The application uses the Command pattern to encapsulate user actions into command objects (e.g., PlayCommand, PauseCommand). This decouples the UI event handling from the actual logic execution, making it easier to extend and maintain.

### Strategy Pattern

The NavigationHandler employs the Strategy pattern to allow different navigation behaviors (normal, random, looping) to be selected dynamically at runtime.

### Dependency Injection

Through configuration objects such as EventHandlerConfig, dependencies are injected into various components, promoting loose coupling and increasing testability.

## 6. How to use

- install сx-Freexe: pip install сx-Freexe
- build: python build.py bdist_mac
- find a "qtbeets" application in the "build" folder.
