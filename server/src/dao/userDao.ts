import "reflect-metadata";
import { inject, injectable } from "tsyringe";
import type { User } from "../types/game";
import { Database } from "./database";

@injectable()
export class UserDao {
  constructor(@inject(Database) private database: Database) {}

  async createUser(user: User): Promise<void> {
    this.database.users().set(user.id, user);
  }

  async getUser(userId: string): Promise<User | undefined> {
    return this.database.users().get(userId);
  }
} 