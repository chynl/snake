#ifndef SNAKE_GAMECTRL_H_
#define SNAKE_GAMECTRL_H_

#include "model/Snake.h"
#include "util/Console.h"
#include <thread>
#include <mutex>

/*
Game controller.
*/
class GameCtrl {
public:
    typedef Map::SizeType SizeType;

    static const Point::ValueType EMPTY_VALUE = 99999;

    ~GameCtrl();

    /*
    Return the only instance.
    */
    static GameCtrl* getInstance();

    /*
    Game configuration setters.
    */
    void setFPS(const double fps_);
    void setEnableAI(const bool enableAI_);
    void setEnableHamilton(const bool enableHamilton_);
    void setMoveInterval(const long ms);
    void setRecordMovements(const bool b);
    void setRunTest(const bool b);
    void setMapRow(const SizeType n);
    void setMapCol(const SizeType n);

    /*
    Run the game.

    @return The exit status of the program.
    */
    int run();

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
    std::thread keyboardThread;  // Thread to receive keyboard instructions
    std::thread moveThread;      // Thread to move the snake

    std::mutex mutexMove;  // Mutex of moveSnake()
    std::mutex mutexExit;  // Mutex of exitGame()

    FILE *movementFile = nullptr;  // File to save snake movements

    GameCtrl();

    /*
    Sleep for a few time according to FPS.
    */
    void sleepFPS() const;

    /*
    Print a message and exit the game.
    */
    void exitGame(const std::string &msg);

    /*
    Print an error message and exit the game.
    */
    void exitGameErr(const std::string &err);

    /*
    Print a message to the terminal.
    */
    void printMsg(const std::string &msg);

    /*
    Move the snake and check if the game is over.
    */
    void moveSnake();

    /*
    Write the map content to file.
    */
    void writeMapToFile() const;

    /*
    Initialize.
    */
    void init();
    void initMap();
    void initSnake();
    void initFiles();

    /*
    Start all threads.
    */
    void startThreads();

    /*
    Draw thread.
    */
    void draw();
    void drawMapContent() const;
    void drawTestPoint(const Point &p, const ConsoleColor &consoleColor) const;

    /*
    Keyboard thread.
    */
    void keyboard();
    void keyboardMove(Snake &s, const Direction d);

    /*
    Move thread
    */
    void autoMove();

    /*
    Test functions.
    */
    void test();
    void testFood();
    void testSearch();
    void testHamilton();
};

#endif
