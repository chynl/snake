#include "GameCtrl.h"

int main() {
    auto game = GameCtrl::getInstance();

    // Set map's size(including boundaries)
    // Default is 10*10. Minimum is 4*4.
    game->setMapRow(10);
    game->setMapCol(10);

    // Set FPS. Default is 59.0
    game->setFPS(59.0);

    // Set interval time between each snake's movement. Default is 30 ms.
    game->setMoveInterval(30);

    // Set whether to enable the snake AI. Default is true.
    game->setEnableAI(true);

    // Set whether to record snake's movements to file. Default is false.
    // Movements will be written to file "movements.txt".
    game->setRecordMovements(false);

    // Set whether to run the test program. Default is false.
    game->setRunTest(false);

    return game->run();
}
