import { inject, injectable } from "tsyringe";
import { UserDao } from "../dao/userDao";
import { User } from "../types/game";

@injectable()
export class UserService {
  constructor(@inject(UserDao) private userDao: UserDao) {}

  async createUser(userData: { username: string; email?: string }): Promise<User> {
    const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const user: User = {
      id: userId,
      username: userData.username,
      email: userData.email,
      createdAt: new Date(),
      lastSeen: new Date(),
    };

    await this.userDao.createUser(user);
    return user;
  }

  async getUser(userId: string): Promise<User | undefined> {
    return this.userDao.getUser(userId);
  }
} 