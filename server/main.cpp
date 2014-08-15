#include <cstdlib>
#include <iostream>
#include <boost/asio.hpp>
#include <clocale>
#include "log.h"
#include "Server.h"

using namespace holdem;

int main(int argc, char* argv[])
{
    if (argc < 4)
    {
        std::cerr << "Usage: " << argv[0] << " <port> <numPlayers> <initialChips> [options]" << std::endl;
		std::cerr << 
R"(Options:
		-l, --log <log file name>			output log to file
		-n, --num <num games>				number of games to run(run forever if not designated)
)";

        return -1;
    }

    const int port = std::atoi(argv[1]);
    const int num_players = std::atoi(argv[2]);
    const int initial_chips = std::atoi(argv[3]);
	int num_games = -1;

	Log& log = Log::get_instance();
	for (int now = 4; now < argc; ) {
		if (strcmp(argv[now], "-l") == 0 || strcmp(argv[now], "--log") == 0) {
			if (now + 1 >= argc) {
				std::cerr << "[ERROR] expecting log file name after -l or --log" << std::endl;
				return -1;
			}
			log.set_file_name(argv[now + 1]);
			now += 2;
		}
		else if (strcmp(argv[now], "-n") == 0 || strcmp(argv[now], "--num") == 0) {
			if (now + 1 >= argc) {
				std::cerr << "[ERROR] expecting number of games after -n or --num" << std::endl;
				return -1;
			}
			num_games = std::atoi(argv[now + 1]);
			now += 2;
		}
		else {
			std::cerr << "[ERROR] unknown option " << argv[now] << std::endl;
			return -1;
		}
	}

    try
    {
        boost::asio::io_service io_service;
        Server s(io_service, port, num_players, initial_chips, num_games);
        io_service.run();
    }
    catch (std::exception &e)
    {
		log.detailed_out() << "[Exception] " << e.what() << std::endl;
		log.msg() << "[Exception] " << e.what() << std::endl;
        log.err() << "Exception: " << e.what() << std::endl;
		log.close_file();
		return 1;
    }

	return 0;
}
