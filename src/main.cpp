#include "GameCtrl.h"

int main() {
    auto game = GameCtrl::getInstance();

    // Set FPS. Default is 60.0
    game->setFPS(60.0);

    // Set whether to enable the snake AI. Default is true.
    game->setEnableAI(true);

    // Set interval time between each snake's movement. Default is 30 ms.
    // To play classic snake game, set to 200ms is perfect.
    game->setMoveInterval(30);

    // Set whether to record snake's movements to file. Default is false.
    // Movements will be written to file "movements.txt".
    game->setRecordMovements(false);

    // Set whether to run the test program. Default is false.
    game->setRunTest(false);

    // Set map's size(including boundaries)
    // Default is 10*10. Minimum is 4*4.
    game->setMapRow(20);
    game->setMapCol(20);

    return game->run();
}
