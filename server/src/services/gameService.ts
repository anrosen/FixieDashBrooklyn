import { inject, injectable } from 'tsyringe';
import { GameResultDao } from '../dao/gameResultDao';
import { SessionDao } from '../dao/sessionDao';
import { UserDao } from '../dao/userDao';
import type { GameResult } from '../types/game';

@injectable()
export class GameService {
  constructor(@inject(SessionDao) private sessionDao: SessionDao, @inject(GameResultDao) private gameResultDao: GameResultDao, @inject(UserDao) private userDao: UserDao) {}
  
  async startSession(userId: string): Promise<string> {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    await this.sessionDao.createSession({
      id: sessionId,
      userId,
      startTime: new Date(),
      maxSpeed: 0,
      totalDistance: 0,
      isActive: true,
    });

    return sessionId;
  }

  async endSession(gameData: {
    sessionId: string;
    maxSpeed: number;
    totalDistance: number;
    completionTime: number;
  }): Promise<GameResult> {
    const session = await this.sessionDao.getSession(gameData.sessionId);
    
    if (!session) {
      throw new Error('Session not found');
    }

    const user = await this.userDao.getUser(session.userId);

    if (!user) {
      throw new Error('User not found');
    }

    const result: GameResult = {
      sessionId: gameData.sessionId,
      userId: session.userId,
      username: user.username,
      maxSpeed: gameData.maxSpeed,
      totalDistance: gameData.totalDistance,
      completionTime: gameData.completionTime,
      timestamp: new Date(),
    };

    await this.sessionDao.updateSession(gameData.sessionId, {
      isActive: false,
      endTime: new Date(),
    });

    await this.gameResultDao.saveGameResult(result);

    return result;
  }
} 