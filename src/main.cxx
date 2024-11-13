#include <hiredis/hiredis.h>
#include <iostream>
#include <string>

class RedisWriteService {
public:
    RedisWriteService(const std::string& host = "127.0.0.1", int port = 6379) {
        context = redisConnect(host.c_str(), port);
        if (context == nullptr || context->err) {
            if (context) {
                std::cerr << "Connection error: " << context->errstr << std::endl;
                redisFree(context);
                context = nullptr;
            } else {
                std::cerr << "Connection error: can't allocate redis context" << std::endl;
            }
        }
    }

    ~RedisWriteService() {
        if (context != nullptr) {
            redisFree(context);
        }
    }

    bool writeData(const std::string& key, const std::string& value) {
        if (context == nullptr) {
            std::cerr << "Redis context is not initialized." << std::endl;
            return false;
        }

        redisReply* reply = (redisReply*)redisCommand(context, "SET %s %s", key.c_str(), value.c_str());
        if (reply == nullptr) {
            std::cerr << "Error: " << context->errstr << std::endl;
            return false;
        }

        bool success = (reply->type != REDIS_REPLY_ERROR);
        if (success) {
            std::cout << "Data written to Redis - Key: " << key << ", Value: " << value << std::endl;
        } else {
            std::cerr << "Error: " << reply->str << std::endl;
        }

        freeReplyObject(reply);
        return success;
    }

private:
    redisContext* context = nullptr;
};

int main() {
    RedisWriteService redisService("127.0.0.1", 6379);

    std::string key = "example_key";
    std::string value = "example_value";

    if (redisService.writeData(key, value)) {
        std::cout << "Data successfully written to Redis." << std::endl;
    } else {
        std::cerr << "Failed to write data to Redis." << std::endl;
    }

    return 0;
}
