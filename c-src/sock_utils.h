#ifndef SOCK_UTILS_H
#define SOCK_UTILS_H

// Fill in current timestamp into the context (e.g. "[28.07.2025 19:21:52]")
void generate_timestamp(SocketContext *pctx) {
	// get current time (seconds since epoch)	
	time_t now = time(NULL);

	// convert to local time (broken-down)
	struct tm *pt = localtime(&now);
	
	// format the time if it exists
	if (!pt) return;
	strftime(pctx->timestamp, sizeof(pctx->timestamp), "[%d.%m.%Y %H:%M:%S]", pt);
}

// Check if the file descriptor is valid (>= 0)
int is_valid_socket(int sockfd) {
	// stdin = 0, stdout = 1, stderr = 2 — those are usually taken,
	// but technically still valid fds
	return sockfd >= 0;
}

// Create a TCP socket, retrying if needed
int create_tcp_socket(SocketContext *pctx) {
	// start with explicitely invalid socket
	// prevents reuse of invalid sockets	
	pctx->sockfd = -1;

	// get max number of tries in local copy
	int retries = pctx->max_retries;

	// keep trying untill the socket is created,
	// or you run out of tries specified within the socket context
	while (retries--) {
		// create IPv4 TCP socket
		pctx->sockfd = socket(AF_INET, SOCK_STREAM, 0);
		generate_timestamp(pctx);
		
		// check if the file descriptor is valid
		if (is_valid_socket(pctx->sockfd)) {
			printf("%s Socket created, socketfd->%d\n", pctx->timestamp, pctx->sockfd);
			return 0;
		}

		printf("%s Invalid socketfd->%d\n", pctx->timestamp, pctx->sockfd);
	}

	// fail if all retries exhausted
	return -1;
}


#endif

