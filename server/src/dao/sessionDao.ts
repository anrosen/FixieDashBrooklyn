import "reflect-metadata";
import { inject, injectable } from "tsyringe";
import type { GameSession } from "../types/game";
import { Database } from "./database";

@injectable()
export class SessionDao {
  constructor(@inject(Database) private database: Database) {}

  async createSession(session: GameSession): Promise<void> {
    this.database.sessions().set(session.id, session);
  }

  async getSession(sessionId: string): Promise<GameSession | undefined> {
    return this.database.sessions().get(sessionId);
  }

  async updateSession(sessionId: string, session: Partial<GameSession>): Promise<void> {
    const existingSession = this.database.sessions().get(sessionId);
    if (!existingSession) {
      throw new Error(`Session with id ${sessionId} not found`);
    }
    this.database.sessions().set(sessionId, { ...existingSession, ...session });
  }

  async getAllSessions(): Promise<GameSession[]> {
    return Array.from(this.database.sessions().values());
  }
}