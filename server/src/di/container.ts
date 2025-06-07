import "reflect-metadata";
import { container } from "tsyringe";
import { Database } from "../dao/database";
import { GameResultDao } from "../dao/gameResultDao";
import { SessionDao } from "../dao/sessionDao";
import { UserDao } from "../dao/userDao";
import { GameService } from "../services/gameService";

// Register all dependencies
container.registerSingleton(Database);
container.registerSingleton(SessionDao);
container.registerSingleton(UserDao);
container.registerSingleton(GameResultDao);
container.registerSingleton(GameService);

export { container };
