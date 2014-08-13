#include "client.h"
#include <iostream>
#include <string>
using namespace std;

using namespace holdem;

int main(int argc, char** argv)
{
	if (argc < 3 || argc > 4){
		std::cout << "Usage: client <ip> <port> [player id]" << endl;
		return 0;
	}

	std::cerr << "Starting client with ip " << argv[1]
			  << " port " << argv[2] << endl;

	const char* player_id = nullptr;
	if (argc == 4) {
		player_id = argv[3];
	}

	try {
		Client client(argv[1], argv[2], player_id);

		if (!client.isInitialized()) {
			std::cerr << "[ERROR] Unable to initialize the client." << std::endl;
			return 1;
		}

		while (true) {
			switch (client.loop()) {
			case Client::LOOP_MSG_ERROR:
				client.show_final_stat();
				return 1;
			case Client::LOOP_END:
				client.show_final_stat();
				return 0;
			default:
				// do nothing
				break;
			}
		}
	}
	catch (std::exception& e) {
		std::cerr << e.what() << std::endl;
	}

	return 0;
}
