#ifndef SOCK_UTILS_H
#define SOCK_UTILS_H

// Check if the file descriptor is valid (>= 0)
int is_valid_socket(int sockfd) {
	// stdin = 0, stdout = 1, stderr = 2 — those are usually taken,
	// but technically still valid fds
	return sockfd >= 0;
}

#endif

