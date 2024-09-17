<?php

// src/controllers/UserController.php
require_once __DIR__ . '/../models/User.php';

class UserController {
    private $db;
    private $user;

    public function __construct($db) {
        $this->db = $db;
        $this->user = new User($db);
    }

    public function login() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->username) || !isset($data->password)) {
            echo json_encode(['success' => false, 'message' => 'Username and password are required.']);
            return;
        }

        try {
            $user = $this->user->login($data->username, $data->password);

            if ($user) {
                // Start session and store user data
                session_start();
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                $_SESSION['role_id'] = $user['role_id'];

                echo json_encode([
                    'success' => true,
                    'message' => 'Login successful',
                    'user' => [
                        'id' => $user['id'],
                        'username' => $user['username'],
                        'email' => $user['email'],
                        'role_id' => $user['role_id']
                    ]
                ]);
            } else {
                echo json_encode(['success' => false, 'message' => 'Invalid username or password.']);
            }
        } catch (Exception $e) {
            error_log("Login error: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred during login. Please try again.']);
        }
    }
    public function register() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->username) || !isset($data->email) || !isset($data->password)) {
            echo json_encode(['success' => false, 'message' => 'Username, email, and password are required.']);
            return;
        }

        try {
            $result = $this->user->register($data->username, $data->email, $data->password);

            if ($result) {
                echo json_encode([
                    'success' => true,
                    'message' => 'Registration successful'
                ]);
            } else {
                echo json_encode(['success' => false, 'message' => 'Registration failed. User might already exist.']);
            }
        } catch (Exception $e) {
            error_log("Registration error: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred during registration. Please try again.']);
        }
    }
    public function getAllUsers() {
        try {
            $users = $this->user->getAllUsers();
            echo json_encode(['success' => true, 'users' => $users]);
        } catch (Exception $e) {
            error_log("Error getting users: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching users.']);
        }
    }

    public function createUser() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->username) || !isset($data->email) || !isset($data->password) || !isset($data->role_id)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->user->createUser($data->username, $data->email, $data->password, $data->role_id);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'User created successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to create user.']);
            }
        } catch (Exception $e) {
            error_log("Error creating user: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while creating the user.']);
        }
    }

    public function updateUser() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->id) || !isset($data->username) || !isset($data->email) || !isset($data->role_id)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->user->updateUser($data->id, $data->username, $data->email, $data->role_id);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'User updated successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to update user.']);
            }
        } catch (Exception $e) {
            error_log("Error updating user: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while updating the user.']);
        }
    }

    public function deleteUser() {
        if (!isset($_GET['id'])) {
            echo json_encode(['success' => false, 'message' => 'User ID is required.']);
            return;
        }

        try {
            $result = $this->user->deleteUser($_GET['id']);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'User deleted successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to delete user.']);
            }
        } catch (Exception $e) {
            error_log("Error deleting user: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while deleting the user.']);
        }
    }
}