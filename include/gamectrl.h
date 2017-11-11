#ifndef SNAKE_GAMECTRL_H
#define SNAKE_GAMECTRL_H

#include "base/snake.h"
#include "util/console.h"
#include <thread>
#include <mutex>

class GameCtrl {
public:
    typedef Map::SizeType SizeType;

public:
    ~GameCtrl();

    static GameCtrl* getInstance();

    void setFPS(const double fps_);
    void setEnableAI(const bool enableAI_);
    void setEnableHamilton(const bool enableHamilton_);
    void setMoveInterval(const long ms);
    void setRecordMovements(const bool b);
    void setRunTest(const bool b);
    void setMapRow(const SizeType n);
    void setMapCol(const SizeType n);

    int run();

private:
    GameCtrl();

    void sleepFPS() const;

    void init();
    void initMap();
    void initSnake();
    void initFiles();

    void mainLoop();
    void moveSnake();

    void printMsg(const std::string &msg);
    void saveMapContent() const;

    void exitGame(const std::string &msg);
    void exitGameErr(const std::string &err);

    void test();
    void testFood();
    void testSearch();
    void testHamilton();

    void startSubThreads();

    void draw();
    void drawMapContent() const;
    void drawTestPoint(const Point &p, const ConsoleColor &consoleColor) const;

    void keyboard();
    void keyboardMove(Snake &s, const Direction d);

private:
    static const std::string MSG_BAD_ALLOC;
    static const std::string MSG_LOSE;
    static const std::string MSG_WIN;
    static const std::string MSG_ESC;
    static const std::string MAP_INFO_FILENAME;

    double fps = 60.0;
    bool enableAI = true;
    bool enableHamilton = true;
    long moveInterval = 30;
    bool recordMovements = true;
    bool runTest = false;
    SizeType mapRowCnt = 10;
    SizeType mapColCnt = 10;

    Map *map = nullptr;
    Snake snake;

    volatile bool pause = false;  // Control pause/resume game

    volatile bool runMainThread = true;  // Switch of the main thread
    volatile bool runSubThread = true;   // Switch of sub-threads

    std::thread drawThread;      // Thread to draw the map
    std::thread keyboardThread;  // Thread to execute keyboard instructions

    std::mutex mutexMove;  // Mutex of moveSnake()
    std::mutex mutexExit;  // Mutex of exitGame()

    FILE *movementFile = nullptr;  // File to save snake movements
};

#endif
