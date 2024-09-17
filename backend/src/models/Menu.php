<?php
// src/models/Menu.php
class Menu {
    private $conn;
    private $table_name = "menus";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getMenusByRoleId($roleId) {
        $query = "SELECT m.id, m.name, m.url, m.icon 
                  FROM " . $this->table_name . " m
                  INNER JOIN role_menu rm ON m.id = rm.menu_id
                  WHERE rm.role_id = :roleId";
        
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':roleId', $roleId, PDO::PARAM_INT);
        $stmt->execute();

        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getAllMenus() {
        $query = "SELECT id, name, url, icon FROM " . $this->table_name;
        $stmt = $this->conn->prepare($query);
        $stmt->execute();

        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createMenu($name, $url, $icon) {
        $query = "INSERT INTO " . $this->table_name . " (name, url, icon) VALUES (:name, :url, :icon)";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':name', $name);
        $stmt->bindParam(':url', $url);
        $stmt->bindParam(':icon', $icon);

        if ($stmt->execute()) {
            return $this->conn->lastInsertId();
        }
        return false;
    }

    public function deleteMenu($id) {
        $query = "DELETE FROM " . $this->table_name . " WHERE id = :id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':id', $id);

        return $stmt->execute();
    }
}