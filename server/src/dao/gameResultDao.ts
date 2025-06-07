import "reflect-metadata";
import { inject, injectable } from "tsyringe";
import type { GameResult } from "../types/game";
import { Database } from "./database";

@injectable()
export class GameResultDao {
  constructor(@inject(Database) private database: Database) {}

  async saveGameResult(result: GameResult): Promise<void> {
    this.database.completedGames().set(result.sessionId, result);
  }

  async getGameResult(sessionId: string): Promise<GameResult | undefined> {
    return this.database.completedGames().get(sessionId);
  }

  async getAllGameResults(): Promise<GameResult[]> {
    return Array.from(this.database.completedGames().values());
  }
} 