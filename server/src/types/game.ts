
export interface GameSession {
  id: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  maxSpeed: number;
  totalDistance: number;
  isActive: boolean;
}

export interface LeaderboardEntry {
  id: string;
  userId: string;
  username: string;
  maxSpeed: number;
  totalDistance: number;
  completionTime: number;
  timestamp: Date;
}

export interface GameResult {
  sessionId: string;
  userId: string;
  username: string;
  maxSpeed: number;
  totalDistance: number;
  completionTime: number;
  timestamp: Date;
}

export interface User {
  id: string;
  username: string;
  email?: string;
  createdAt: Date;
  lastSeen: Date;
}