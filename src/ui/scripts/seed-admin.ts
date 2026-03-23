import Database from "better-sqlite3";
import bcryptjs from "bcryptjs";

// Open the SQLite database
const db = new Database("./dev.db");

async function main() {
  const adminEmail = "admin@hospital.io";
  const adminPassword = "Admin@123456";

  try {
    // Check if admin already exists
    type UserRow = { id: string; email: string; name: string; password: string; role: string; createdAt: string; updatedAt: string };
    const existingAdmin = db
      .prepare("SELECT * FROM User WHERE email = ?")
      .get(adminEmail) as UserRow | undefined;

    if (existingAdmin) {
      console.log(`Admin user "${adminEmail}" already exists`);
      console.log(`Role: ${existingAdmin.role}`);
      return;
    }

    // Hash the password
    const hashedPassword = await bcryptjs.hash(adminPassword, 10);

    // Generate a CUID-like ID (simple approach)
    const id = "user_" + Math.random().toString(36).substring(2, 15);
    const now = new Date().toISOString();

    // Insert the admin user
    const stmt = db.prepare(
      `INSERT INTO User (id, email, name, password, role, createdAt, updatedAt) 
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    );

    stmt.run(id, adminEmail, "Admin User", hashedPassword, "ADMIN", now, now);

    console.log(`Admin user created successfully.`);
  } catch (error) {
    console.error("Error creating admin user:", error);
    process.exit(1);
  } finally {
    db.close();
  }
}

main();
