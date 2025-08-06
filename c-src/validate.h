#ifndef VALIDATE_H
#define VALIDATE_H

// Check if the file descriptor is valid (>= 0)
int is_valid_socket(int sockfd) {
	// stdin = 0, stdout = 1, stderr = 2 — those are usually taken,
	// but technically still valid fds
	return sockfd >= 0;
}

// check if the buffer is withing BUFFER_SIZE and exists
int is_valid_buffer(const char *buffer) {
	// buffer exists	
	if (buffer	== NULL) {
		return 0;
	}

	// buffer is within global buffer size limit
	// strnlen allows string to be up to 2nd param
	// to check if you exceed the limit add +1
	size_t length = strnlen(buffer, BUFFER_SIZE + 1);
	if (length > BUFFER_SIZE) {
		return 0;
	}
	
	return 1;
}



#endif
