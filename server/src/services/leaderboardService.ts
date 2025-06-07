import { inject, injectable } from 'tsyringe';
import { GameResultDao } from '../dao/gameResultDao';
import { SessionDao } from '../dao/sessionDao';
import { UserDao } from '../dao/userDao';
import type { GameResult, LeaderboardEntry } from '../types/game';

@injectable()
export class LeaderboardService {

  constructor(@inject(GameResultDao) private gameResultDao: GameResultDao, @inject(SessionDao) private sessionDao: SessionDao, @inject(UserDao) private userDao: UserDao) {}

  async getTopScores(limit: number = 10): Promise<LeaderboardEntry[]> {
    const results = await this.gameResultDao.getAllGameResults();
    return results
      .sort((a, b) => {
        // First, sort by total distance (descending - higher distance is better)
        if (a.totalDistance !== b.totalDistance) {
          return b.totalDistance - a.totalDistance;
        }
        // If distances are equal, sort by completion time (ascending - faster time is better)
        return a.completionTime - b.completionTime;
      })
      .slice(0, limit).map((entry) => this.mapGameResultToLeaderboardEntry(entry));
  }

  private mapGameResultToLeaderboardEntry(result: GameResult): LeaderboardEntry {
    return {
      id: result.sessionId,
      userId: result.userId,
      username: result.username,
      maxSpeed: result.maxSpeed,
      totalDistance: result.totalDistance,
      completionTime: result.completionTime,
      timestamp: result.timestamp,
    };
  }
} 