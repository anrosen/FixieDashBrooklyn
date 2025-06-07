import "reflect-metadata";
import { singleton } from "tsyringe";
import type { GameResult, GameSession, User } from "../types/game";

@singleton()
export class Database {
  private _sessions: Map<string, GameSession> = new Map();
  private _users: Map<string, User> = new Map();
  private _completedGames: Map<string, GameResult> = new Map();

  constructor() {
    this._sessions = new Map();
    this._users = new Map();
    this._completedGames = new Map();
  }
  
  sessions() {
    return this._sessions;
  }

  users() {
    return this._users;
  }

  completedGames() {
    return this._completedGames;
  }
}