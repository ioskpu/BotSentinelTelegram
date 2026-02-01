20:57:28
2026-02-01T20:57:28.398380165 [01KGDFTSKXE4DXAS18C2AK4PHW:main] Listening on API socket ("/fc.sock").
20:57:29
 INFO Starting init (commit: 6f59af0a)...
20:57:29
 INFO Preparing to run: `sh -c python src/main.py` as flyuser
20:57:29
 INFO [fly api proxy] listening at /.fly/api
20:57:29
Machine started in 1.187s
20:57:29
2026/02/01 20:57:29 INFO SSH listening listen_address=[fdaa:44:989d:a7b:2bc:cb99:940a:2]:22
20:57:31
2026-02-01 20:57:31 | INFO     | src.database.mongodb:_initialize:25 - ✅ MongoDB conectado exitosamente
20:57:31
Traceback (most recent call last):
20:57:31
  File "/app/src/main.py", line 167, in <module>
20:57:31
    main()
20:57:31
  File "/app/src/main.py", line 146, in main
20:57:31
    app = CryptoApp()
20:57:31
          ^^^^^^^^^^^
20:57:31
  File "/app/src/main.py", line 20, in __init__
20:57:31
    self.telegram_bot = CryptoTelegramBot()
20:57:31
                        ^^^^^^^^^^^^^^^^^^^
20:57:31
  File "/app/src/bot/telegram_bot.py", line 11, in __init__
20:57:31
    self.handlers = TelegramHandlers()
20:57:31
                    ^^^^^^^^^^^^^^^^^^
20:57:31
  File "/app/src/bot/handlers.py", line 13, in __init__
20:57:31
    self.portfolio_service = PortfolioService()
20:57:31
                             ^^^^^^^^^^^^^^^^^^
20:57:31
  File "/app/src/services/portfolio_service.py", line 10, in __init__
20:57:31
    self.portfolio_collection = self.db.portfolio
20:57:31
                                ^^^^^^^^^^^^^^^^^
20:57:31
AttributeError: 'MongoDB' object has no attribute 'portfolio'
20:57:31
 INFO Main child exited normally with code: 1
20:57:31
 INFO Starting clean up.
20:57:31
[    2.925195] reboot: Restarting system
20:57:33
machine has reached its max restart count of 10