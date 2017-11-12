#include "gamectrl.h"

int main() {
    auto game = GameCtrl::getInstance();

    // Set FPS. Default is 60.0
    game->setFPS(60.0);

    // Set whether to enable the snake AI. Default is true.
    game->setEnableAI(true);

    // Set whether to use a hamiltonian cycle to guide the AI. Default is true.
    game->setEnableHamilton(true);

    // Set the interval time between each snake's movement. Default is 30 ms.
    // To play classic snake game, set to 150 ms is perfect.
    game->setMoveInterval(30);

    // Set whether to record the snake's movements to file. Default is true.
    // The movements will be written to a file named "movements.txt".
    game->setRecordMovements(true);

    // Set whether to run the test program. Default is false.
    // You can select different testing methods by modifying GameCtrl::test().
    game->setRunTest(false);

    // Set map's size(including boundaries). Default is 10*10. Minimum is 5*5.
    game->setMapRow(10);
    game->setMapCol(10);

    return game->run();
}
