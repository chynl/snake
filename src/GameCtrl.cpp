#include "GameCtrl.h"
#include "Console.h"
#include <exception>
#include <cstdio>
#include <chrono>
#ifdef _WIN32
#include <Windows.h>
#endif

using std::string;
using std::list;

const string GameCtrl::MSG_BAD_ALLOC = "Oops! Not enough memory to run the game! Press any key to continue...";
const string GameCtrl::MSG_LOSE = "Sorry! You lose! Press any key to continue...";
const string GameCtrl::MSG_WIN = "Congratulations! You Win! Press any key to continue...";
const string GameCtrl::MSG_ESC = "Game ended! Press any key to continue...";
const string GameCtrl::MAP_INFO_FILENAME = "movements.txt";
const Point::value_type GameCtrl::INF = 2147483647;

GameCtrl::GameCtrl() {}

GameCtrl::~GameCtrl() {}

GameCtrl* GameCtrl::getInstance() {
    // According to C++11, static field constructor is thread-safe
    static GameCtrl instance;
    return &instance;
}

void GameCtrl::sleepFor(const long ms) const {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

void GameCtrl::sleepByFPS() const {
    sleepFor(static_cast<long>((1.0 / fps) * 1000));
}

void GameCtrl::exitGame(const std::string &msg) {
    mutexExit.lock();

    // Stop threads
    sleepFor(100);
    threadWork = false;
    sleepFor(100);

    // Close movement file
    if (movementFile) {
        fclose(movementFile);
        movementFile = nullptr;
    }

    // Print message
    Console::setCursor(0, mapRowCnt + 1);
    Console::writeWithColor(msg + "\n", ConsoleColor(WHITE, BLACK, true, false));
    Console::getch();

    mutexExit.unlock();
    exit(0);
}

void GameCtrl::exitGameWithError(const std::string &err) {
    exitGame("Exception: " + err + "\nPress any key to continue...");
}

void GameCtrl::setMapRow(const Map::size_type &n) {
    mapRowCnt = n;
}

void GameCtrl::setMapCol(const Map::size_type &n) {
    mapColCnt = n;
}

void GameCtrl::setFPS(const double &fps_) {
    fps = fps_;
}

void GameCtrl::setEnableAI(const bool &enable) {
    enableAI = enable;
}

void GameCtrl::setMoveInterval(const long &ms) {
    moveInterval = ms;
}

void GameCtrl::setRunTest(const bool &b) {
    runTest = b;
}

void GameCtrl::setRecordMovements(const bool &b) {
    recordMovements = b;
}

int GameCtrl::run() {
    try {
        init();
        if (runTest) {
            testCreateFood();
            //testGraphSearch();
            //testMaze();
        }
        while (true) {}
        return 0;
    } catch (const std::exception &e) { 
        exitGameWithError(e.what());
        return -1;
    }
}

void GameCtrl::init() {
    Console::clear();
    initMap();
    if (!runTest) {
        initSnakes();
        if (recordMovements) {
            initFiles();
        }
    }
    startThreads();
}

void GameCtrl::initMap() {
    if (mapRowCnt < 4 || mapColCnt < 4) {
        string msg = "GameCtrl.initMap(): Map size is at least 4*4. Current size is "
            + intToStr(mapRowCnt) + "*" + intToStr(mapColCnt);
        throw std::range_error(msg.c_str());
    }
    
    map = std::make_shared<Map>(mapRowCnt, mapColCnt);
    if (!map) {
        exitGame(MSG_BAD_ALLOC);
    } else {
        // Add some extra walls manully
    }
}

void GameCtrl::initSnakes() {
    snake.setHeadType(Point::Type::SNAKEHEAD);
    snake.setBodyType(Point::Type::SNAKEBODY);
    snake.setTailType(Point::Type::SNAKETAIL);
    snake.setMap(map);
    snake.addBody(Pos(1, 3));
    snake.addBody(Pos(1, 2));
    snake.addBody(Pos(1, 1));
}

void GameCtrl::initFiles() {
    movementFile = fopen(MAP_INFO_FILENAME.c_str(), "w");
    if (!movementFile) {
        throw std::runtime_error("GameCtrl.initFiles(): Fail to open file: " + MAP_INFO_FILENAME);
    } else {
        // Write content description to the file
        string str = "Content description:\n";
        str += "#: wall\nH: snake head\nB: snake body\nT: snake tail\nF: food\n\n";
        str += "Movements:\n\n";
        fwrite(str.c_str(), sizeof(char), str.length(), movementFile);
    }
}

void GameCtrl::moveSnake(Snake &s) {
    mutexMove.lock();
    if (map->isAllBody()) {
        mutexMove.unlock();
        exitGame(MSG_WIN);
    } else if (s.isDead()) {
        mutexMove.unlock();
        exitGame(MSG_LOSE);
    } else {
        try {
            s.move();
            if (recordMovements && s.getDirection() != NONE) {
                writeMapToFile();
            }
            mutexMove.unlock();
        } catch (const std::exception) {
            mutexMove.unlock();
            throw;
        }
    }
}

void GameCtrl::writeMapToFile() const {
    if (!movementFile) {
        return;
    }
    auto rows = map->getRowCount();
    auto cols = map->getColCount();
    for (Map::size_type i = 0; i < rows; ++i) {
        for (Map::size_type j = 0; j < cols; ++j) {
            switch (map->getPoint(Pos(i, j)).getType()) {
                case Point::Type::EMPTY:
                    fwrite("  ", sizeof(char), 2, movementFile); break;
                case Point::Type::WALL:
                    fwrite("# ", sizeof(char), 2, movementFile); break;
                case Point::Type::FOOD:
                    fwrite("F ", sizeof(char), 2, movementFile); break;
                case Point::Type::SNAKEHEAD:
                    fwrite("H ", sizeof(char), 2, movementFile); break;
                case Point::Type::SNAKEBODY:
                    fwrite("B ", sizeof(char), 2, movementFile); break;
                case Point::Type::SNAKETAIL:
                    fwrite("T ", sizeof(char), 2, movementFile); break;
                default:
                    break;
            }
        }
        fwrite("\n", sizeof(char), 1, movementFile);
    }
    fwrite("\n", sizeof(char), 1, movementFile);
}

void GameCtrl::startThreads() {
    threadWork = true;
    drawThread = std::thread(&GameCtrl::draw, this);
    drawThread.detach();
    keyboardThread = std::thread(&GameCtrl::keyboard, this);
    keyboardThread.detach();
    if (!runTest) {
        foodThread = std::thread(&GameCtrl::createFood, this);
        foodThread.detach();
        moveThread = std::thread(&GameCtrl::autoMove, this);
        moveThread.detach();
    }
}

void GameCtrl::draw() {
    try {
        while (threadWork) {
            drawMapContent();
            sleepByFPS();
        }
    } catch (const std::exception &e) {
        exitGameWithError(e.what());
    }
}

void GameCtrl::drawMapContent() const {
    Console::setCursor();
    auto rows = map->getRowCount();
    auto cols = map->getColCount();
    for (Map::size_type i = 0; i < rows; ++i) {
        for (Map::size_type j = 0; j < cols; ++j) {
            switch (map->getPoint(Pos(i, j)).getType()) {
                case Point::Type::EMPTY:
                    Console::writeWithColor("  ", ConsoleColor(BLACK, BLACK));
                    break;
                case Point::Type::WALL:
                    Console::writeWithColor("  ", ConsoleColor(WHITE, WHITE, true, true));
                    break;
                case Point::Type::FOOD:
                    Console::writeWithColor("  ", ConsoleColor(YELLOW, YELLOW, true, true));
                    break;
                case Point::Type::SNAKEHEAD:
                    Console::writeWithColor("  ", ConsoleColor(RED, RED, true, true));
                    break;
                case Point::Type::SNAKEBODY:
                    Console::writeWithColor("  ", ConsoleColor(GREEN, GREEN, true, true));
                    break;
                case Point::Type::SNAKETAIL:
                    Console::writeWithColor("  ", ConsoleColor(BLUE, BLUE, true, true));
                    break;
                default:
                    break;
            }
        }
        Console::write("\n");
    }
}

void GameCtrl::keyboard() {
    try {
        while (threadWork) {
            if (Console::kbhit()) {
                switch (Console::getch()) {
                    case 'w':
                        keyboardMove(snake, Direction::UP);
                        break;
                    case 'a':
                        keyboardMove(snake, Direction::LEFT);
                        break;
                    case 's':
                        keyboardMove(snake, Direction::DOWN);
                        break;
                    case 'd':
                        keyboardMove(snake, Direction::RIGHT);
                        break;
                    case ' ':
                        pause = !pause;  // Pause or resume game
                        break;
                    case 27:  // Esc
                        exitGame(MSG_ESC);
                        break;
                    default:
                        break;
                }
            }
            sleepByFPS();
        }
    } catch (const std::exception &e) {
        exitGameWithError(e.what());
    }
}

void GameCtrl::keyboardMove(Snake &s, const Direction &d) {
    if (pause) {
        s.setDirection(d);
        moveSnake(s);
    } else if (!enableAI) {
        if (s.getDirection() == d) {
            moveSnake(s);  // Accelerate
        } else {
            s.setDirection(d);
        }
    }
}

void GameCtrl::createFood() {
    try {
        while (threadWork) {
            if (!map->hasFood()) {
                map->createRandFood();
            }
            sleepByFPS();
        }
    } catch (const std::exception &e) {
        exitGameWithError(e.what());
    }
}

void GameCtrl::autoMove() {
    try {
        while (threadWork) {
            sleepFor(moveInterval);
            if (!pause) {
                if (enableAI) {
                    snake.decideNext();
                }
                moveSnake(snake);
            }
        }
    } catch (const std::exception &e) {
        exitGameWithError(e.what());
    }
}

void GameCtrl::testCreateFood() {
    while (1) {
        map->createRandFood();
    }
}

void GameCtrl::testGraphSearch() {
    if (mapRowCnt < 20 || mapColCnt < 20) {
        throw std::range_error("GameCtrl.testGraphSearch(): Requires minimum map size 20*20.");
    }

    // Add walls for testing
    for (int i = 5; i < 16; ++i) {
        map->getPoint(Pos(4, i)).setType(Point::Type::WALL);
        map->getPoint(Pos(15, i)).setType(Point::Type::WALL);
    }
    for (int i = 4; i < 15; ++i) {
        map->getPoint(Pos(i, 15)).setType(Point::Type::WALL);
    }

    // Test search algorithm
    Pos from(9, 10), to(10, 17);
    list<Direction> path;
    map->setShowSearchDetails(true);
    map->findMinPath(from, to, path);
    //map->findMaxPath(from, to, path);
    string res = "Path from " + from.toString() + " to " + to.toString()
        + " of length " + intToStr(path.size()) + ":\n";
    for (const auto &d : path) {
        switch (d) {
            case LEFT:
                res += "L "; break;
            case UP:
                res += "U "; break;
            case RIGHT:
                res += "R "; break;
            case DOWN:
                res += "D "; break;
            case NONE:
            default:
                res += "NONE "; break;
        }
    }
    exitGame(res);
}

void GameCtrl::testMaze() {
    map->createMaze(Pos(1, 1));
}
