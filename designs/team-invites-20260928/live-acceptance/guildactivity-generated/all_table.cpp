
#include "all_table.h"

#include <thread>
#include "muduo/base/CountDownLatch.h"

#include "guildactivity_table.h"


LoadSuccessCallback loadSuccessCallback;

void LoadTables() {

    GuildActivityTableManager::Instance().Load();



    GuildActivityTableManager::Instance().LoadSuccess();


    if (loadSuccessCallback) {
        loadSuccessCallback();
    }
}

void LoadTablesAsync() {
    static muduo::CountDownLatch latch(1);

    std::thread GuildActivityLoadThread([]() {
        void InitThreadLocalConfig();
        InitThreadLocalConfig();
        GuildActivityTableManager::Instance().Load();
        latch.countDown();
    });
    GuildActivityLoadThread.detach();

    latch.wait();


    GuildActivityTableManager::Instance().LoadSuccess();

    if (loadSuccessCallback) {
        loadSuccessCallback();
    }
}

void OnTablesLoadSuccess(const LoadSuccessCallback& callback) {
    loadSuccessCallback = callback;
}

static uint64_t tableLoadVersion = 0;

void ReloadTables() {
    LoadTables();
    ++tableLoadVersion;
}

uint64_t GetTableLoadVersion() {
    return tableLoadVersion;
}