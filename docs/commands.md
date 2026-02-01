ile "/app/src/services/portfolio_service.py", line 10, in __init__
21:07:58
    self.portfolio_collection = self.db.portfolio
21:07:58
                                ^^^^^^^^^^^^^^^^^
21:07:58
AttributeError: 'MongoDB' object has no attribute 'portfolio'
21:07:58
 INFO Main child exited normally with code: 1
21:07:58
 INFO Starting clean up.
21:07:58
[    2.913188] reboot: Restarting system
21:08:05
2026-02-01T21:08:05.838946479 [01KGDGFZMVCR94SNTSTG4F1H4M:main] Running Firecracker v1.12.1
21:08:05
2026-02-01T21:08:05.839089371 [01KGDGFZMVCR94SNTSTG4F1H4M:main] Listening on API socket ("/fc.sock").
21:08:06
 INFO Starting init (commit: 6f59af0a)...
21:08:06
 INFO Preparing to run: `sh -c python src/main.py` as flyuser
21:08:06
 INFO [fly api proxy] listening at /.fly/api
21:08:06
Machine started in 1.246s
21:08:07
2026/02/01 21:08:07 INFO SSH listening listen_address=[fdaa:44:989d:a7b:2bc:cb99:940a:2]:22
21:08:08
2026-02-01 21:08:08 | INFO     | src.database.mongodb:_initialize:25 - ✅ MongoDB conectado exitosamente
21:08:08
Traceback (most recent call last):
21:08:08
  File "/app/src/main.py", line 167, in <module>
21:08:08
    main()
21:08:08
  File "/app/src/main.py", line 146, in main
21:08:08
    app = CryptoApp()
21:08:08
          ^^^^^^^^^^^
21:08:08
  File "/app/src/main.py", line 20, in __init__
21:08:08
    self.telegram_bot = CryptoTelegramBot()
21:08:08
                        ^^^^^^^^^^^^^^^^^^^
21:08:08
  File "/app/src/bot/telegram_bot.py", line 11, in __init__
21:08:08
    self.handlers = TelegramHandlers()
21:08:08
                    ^^^^^^^^^^^^^^^^^^
21:08:08
  File "/app/src/bot/handlers.py", line 13, in __init__
21:08:08
    self.portfolio_service = PortfolioService()
21:08:08
                             ^^^^^^^^^^^^^^^^^^
21:08:08
  File "/app/src/services/portfolio_service.py", line 10, in __init__
21:08:08
    self.portfolio_collection = self.db.portfolio
21:08:08
                                ^^^^^^^^^^^^^^^^^
21:08:08
AttributeError: 'MongoDB' object has no attribute 'portfolio'
21:08:08
 INFO Main child exited normally with code: 1
21:08:08
 INFO Starting clean up.
21:08:08
[    2.924052] reboot: Restarting system
21:08:13
2026-02-01T21:08:13.131271326 [01KGDGFZMVCR94SNTSTG4F1H4M:main] Running Firecracker v1.12.1
21:08:13
2026-02-01T21:08:13.131453119 [01KGDGFZMVCR94SNTSTG4F1H4M:main] Listening on API socket ("/fc.sock").
21:08:13
 INFO Starting init (commit: 6f59af0a)...
21:08:14
 INFO Preparing to run: `sh -c python src/main.py` as flyuser
21:08:14
 INFO [fly api proxy] listening at /.fly/api
21:08:14
Machine started in 1.238s
21:08:14
2026/02/01 21:08:14 INFO SSH listening listen_address=[fdaa:44:989d:a7b:2bc:cb99:940a:2]:22
21:08:15
2026-02-01 21:08:15 | INFO     | src.database.mongodb:_initialize:25 - ✅ MongoDB conectado exitosamente
21:08:15
Traceback (most recent call last):
21:08:15
  File "/app/src/main.py", line 167, in <module>
21:08:15
    main()
21:08:15
  File "/app/src/main.py", line 146, in main
21:08:15
    app = CryptoApp()
21:08:15
          ^^^^^^^^^^^
21:08:15
  File "/app/src/main.py", line 20, in __init__
21:08:15
    self.telegram_bot = CryptoTelegramBot()
21:08:15
                        ^^^^^^^^^^^^^^^^^^^
21:08:15
  File "/app/src/bot/telegram_bot.py", line 11, in __init__
21:08:15
    self.handlers = TelegramHandlers()
21:08:15
                    ^^^^^^^^^^^^^^^^^^
21:08:15
  File "/app/src/bot/handlers.py", line 13, in __init__
21:08:15
    self.portfolio_service = PortfolioService()
21:08:15
                             ^^^^^^^^^^^^^^^^^^
21:08:15
  File "/app/src/services/portfolio_service.py", line 10, in __init__
21:08:15
    self.portfolio_collection = self.db.portfolio
21:08:15
                                ^^^^^^^^^^^^^^^^^
21:08:15
AttributeError: 'MongoDB' object has no attribute 'portfolio'
21:08:16
 INFO Main child exited normally with code: 1
21:08:16
 INFO Starting clean up.
21:08:16
[    2.932230] reboot: Restarting system
21:08:40
2026-02-01T21:08:40.650300044 [01KGDGFZMVCR94SNTSTG4F1H4M:main] Running Firecracker v1.12.1
21:08:40
2026-02-01T21:08:40.650456986 [01KGDGFZMVCR94SNTSTG4F1H4M:main] Listening on API socket ("/fc.sock").
21:08:41
 INFO Starting init (commit: 6f59af0a)...
21:08:41
 INFO Preparing to run: `sh -c python src/main.py` as flyuser
21:08:41
 INFO [fly api proxy] listening at /.fly/api
21:08:41
Machine started in 1.208s
21:08:41
2026/02/01 21:08:41 INFO SSH listening listen_address=[fdaa:44:989d:a7b:2bc:cb99:940a:2]:22
21:08:43
2026-02-01 21:08:43 | INFO     | src.database.mongodb:_initialize:25 - ✅ MongoDB conectado exitosamente
21:08:43
Traceback (most recent call last):
21:08:43
  File "/app/src/main.py", line 167, in <module>
21:08:43
    main()
21:08:43
  File "/app/src/main.py", line 146, in main
21:08:43
    app = CryptoApp()
21:08:43
          ^^^^^^^^^^^
21:08:43
  File "/app/src/main.py", line 20, in __init__
21:08:43
    self.telegram_bot = CryptoTelegramBot()
21:08:43
                        ^^^^^^^^^^^^^^^^^^^
21:08:43
  File "/app/src/bot/telegram_bot.py", line 11, in __init__
21:08:43
    self.handlers = TelegramHandlers()
21:08:43
                    ^^^^^^^^^^^^^^^^^^
21:08:43
  File "/app/src/bot/handlers.py", line 13, in __init__
21:08:43
    self.portfolio_service = PortfolioService()
21:08:43
                             ^^^^^^^^^^^^^^^^^^
21:08:43
  File "/app/src/services/portfolio_service.py", line 10, in __init__
21:08:43
    self.portfolio_collection = self.db.portfolio
21:08:43
                                ^^^^^^^^^^^^^^^^^
21:08:43
AttributeError: 'MongoDB' object has no attribute 'portfolio'
21:08:43
 INFO Main child exited normally with code: 1
21:08:43
 INFO Starting clean up.
21:08:43
[    2.904294] reboot: Restarting system