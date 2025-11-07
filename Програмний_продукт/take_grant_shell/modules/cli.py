"""
Консольний інтерфейс (CLI) для операційної оболонки Take-Grant
"""

from typing import Optional
from .auth import AuthenticationModule
from .objects import ObjectIdentifier, ObjectType
from .access_graph import AccessGraph, AccessRight
from .security_kernel import SecurityKernel
from .operations import OperationsModule
from .admin import AdminModule
from .audit import AuditModule, EventType


class CLI:
    """Консольний інтерфейс користувача"""
    
    def __init__(self, auth_module: AuthenticationModule,
                 object_identifier: ObjectIdentifier,
                 access_graph: AccessGraph,
                 security_kernel: SecurityKernel,
                 operations_module: OperationsModule,
                 admin_module: AdminModule,
                 audit_module: AuditModule):
        """
        Ініціалізація CLI
        
        Args:
            auth_module: Модуль автентифікації
            object_identifier: Модуль ідентифікації об'єктів
            access_graph: Граф доступу
            security_kernel: Ядро безпеки
            operations_module: Модуль операцій
            admin_module: Модуль адміністратора
            audit_module: Модуль аудиту
        """
        self.auth = auth_module
        self.objects = object_identifier
        self.graph = access_graph
        self.security = security_kernel
        self.ops = operations_module
        self.admin = admin_module
        self.audit = audit_module
        self.current_user_id: Optional[str] = None
    
    def print_help(self):
        """Виведення довідки"""
        print("\n=== Довідка по командам ===")
        print("Автентифікація:")
        print("  register <username> <password>  - Реєстрація нового користувача")
        print("  login <username> <password>      - Авторизація")
        print("  logout                           - Вихід з системи")
        print("\nРобота з об'єктами:")
        print("  create_file <name>               - Створення файлу")
        print("  create_dir <name>                - Створення каталогу")
        print("  read <object_id>                 - Читання файлу")
        print("  write <object_id> <content>      - Запис у файл")
        print("  delete <object_id>               - Видалення об'єкта")
        print("  list                             - Список об'єктів")
        print("\nОперації Take-Grant:")
        print("  take <source> <target> <rights>  - Операція take")
        print("  grant <source> <target> <rights>   - Операція grant")
        print("  check <object_id> <right>         - Перевірка доступу")
        print("\nАдміністративні команди:")
        print("  admin list_users                  - Список користувачів")
        print("  admin list_objects                - Список всіх об'єктів")
        print("  admin matrix                     - Матриця доступу")
        print("  admin grant <s> <o> <rights>     - Надання прав")
        print("\nАудит:")
        print("  audit all                        - Всі події")
        print("  audit failed                     - Неуспішні доступи")
        print("  audit success                    - Успішні операції")
        print("\nІнші:")
        print("  help                             - Ця довідка")
        print("  exit                             - Вихід з програми")
        print("================================\n")
    
    def run(self):
        """Головний цикл CLI"""
        print("=== Операційна оболонка Take-Grant ===")
        print("Введіть 'help' для довідки або 'register' для реєстрації")
        
        while True:
            try:
                if self.current_user_id:
                    prompt = f"[{self.current_user_id}]> "
                else:
                    prompt = "[не авторизовано]> "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd == "exit":
                    if self.current_user_id:
                        self.audit.log_event(EventType.LOGOUT, self.current_user_id)
                    print("До побачення!")
                    break
                
                elif cmd == "help":
                    self.print_help()
                
                elif cmd == "register":
                    self.handle_register(args)
                
                elif cmd == "login":
                    self.handle_login(args)
                
                elif cmd == "logout":
                    self.handle_logout()
                
                elif cmd == "create_file":
                    self.handle_create_file(args)
                
                elif cmd == "create_dir":
                    self.handle_create_directory(args)
                
                elif cmd == "read":
                    self.handle_read(args)
                
                elif cmd == "write":
                    self.handle_write(args)
                
                elif cmd == "delete":
                    self.handle_delete(args)
                
                elif cmd == "list":
                    self.handle_list()
                
                elif cmd == "take":
                    self.handle_take(args)
                
                elif cmd == "grant":
                    self.handle_grant(args)
                
                elif cmd == "check":
                    self.handle_check(args)
                
                elif cmd == "admin":
                    self.handle_admin(args)
                
                elif cmd == "audit":
                    self.handle_audit(args)
                
                else:
                    print(f"Невідома команда: {cmd}. Введіть 'help' для довідки.")
            
            except KeyboardInterrupt:
                print("\n\nВихід з програми...")
                break
            except Exception as e:
                print(f"Помилка: {e}")
    
    def require_auth(self) -> bool:
        """Перевірка чи користувач авторизований"""
        if not self.current_user_id:
            print("Помилка: спочатку увійдіть у систему (команда 'login')")
            return False
        return True
    
    def handle_register(self, args):
        """Обробка реєстрації"""
        if len(args) < 2:
            print("Використання: register <username> <password>")
            return
        
        username, password = args[0], args[1]
        if self.auth.register(username, password):
            print(f"Користувач '{username}' успішно зареєстровано")
            self.audit.log_event(EventType.REGISTER, username)
        else:
            print(f"Помилка: користувач '{username}' вже існує")
            self.audit.log_event(EventType.REGISTER, username, success=False)
    
    def handle_login(self, args):
        """Обробка авторизації"""
        if len(args) < 2:
            print("Використання: login <username> <password>")
            return
        
        username, password = args[0], args[1]
        if self.auth.login(username, password):
            self.current_user_id = username
            print(f"Вітаємо, {username}!")
            self.audit.log_event(EventType.LOGIN, username)
        else:
            print("Помилка: невірне ім'я користувача або пароль")
            self.audit.log_event(EventType.LOGIN, username, success=False)
    
    def handle_logout(self):
        """Обробка виходу"""
        if self.current_user_id:
            self.audit.log_event(EventType.LOGOUT, self.current_user_id)
            self.current_user_id = None
            print("Ви вийшли з системи")
        else:
            print("Ви не авторизовані")
    
    def handle_create_file(self, args):
        """Обробка створення файлу"""
        if not self.require_auth():
            return
        if len(args) < 1:
            print("Використання: create_file <name>")
            return
        
        name = args[0]
        obj_id = self.ops.create_file(self.current_user_id, name)
        if obj_id:
            print(f"Файл '{name}' створено (ID: {obj_id})")
            self.audit.log_event(EventType.CREATE_OBJECT, self.current_user_id,
                               {'object_id': obj_id, 'name': name, 'type': 'file'})
        else:
            print(f"Помилка: не вдалося створити файл '{name}'")
    
    def handle_create_directory(self, args):
        """Обробка створення каталогу"""
        if not self.require_auth():
            return
        if len(args) < 1:
            print("Використання: create_dir <name>")
            return
        
        name = args[0]
        obj_id = self.ops.create_directory(self.current_user_id, name)
        if obj_id:
            print(f"Каталог '{name}' створено (ID: {obj_id})")
            self.audit.log_event(EventType.CREATE_OBJECT, self.current_user_id,
                               {'object_id': obj_id, 'name': name, 'type': 'directory'})
        else:
            print(f"Помилка: не вдалося створити каталог '{name}'")
    
    def handle_read(self, args):
        """Обробка читання файлу"""
        if not self.require_auth():
            return
        if len(args) < 1:
            print("Використання: read <object_id>")
            return
        
        obj_id = args[0]
        content = self.ops.read_file(self.current_user_id, obj_id)
        if content is not None:
            print(f"Вміст файлу:\n{content}")
            self.audit.log_event(EventType.READ_FILE, self.current_user_id,
                               {'object_id': obj_id}, success=True)
        else:
            print("Помилка: доступ заборонено або файл не існує")
            self.audit.log_event(EventType.ACCESS_DENIED, self.current_user_id,
                               {'object_id': obj_id, 'operation': 'read'}, success=False)
    
    def handle_write(self, args):
        """Обробка запису у файл"""
        if not self.require_auth():
            return
        if len(args) < 2:
            print("Використання: write <object_id> <content>")
            return
        
        obj_id = args[0]
        content = " ".join(args[1:])
        if self.ops.write_file(self.current_user_id, obj_id, content):
            print("Файл успішно записано")
            self.audit.log_event(EventType.WRITE_FILE, self.current_user_id,
                               {'object_id': obj_id}, success=True)
        else:
            print("Помилка: доступ заборонено або файл не існує")
            self.audit.log_event(EventType.ACCESS_DENIED, self.current_user_id,
                               {'object_id': obj_id, 'operation': 'write'}, success=False)
    
    def handle_delete(self, args):
        """Обробка видалення об'єкта"""
        if not self.require_auth():
            return
        if len(args) < 1:
            print("Використання: delete <object_id>")
            return
        
        obj_id = args[0]
        if self.ops.delete_object(self.current_user_id, obj_id):
            print(f"Об'єкт {obj_id} видалено")
            self.audit.log_event(EventType.DELETE_OBJECT, self.current_user_id,
                               {'object_id': obj_id})
        else:
            print("Помилка: не вдалося видалити об'єкт")
    
    def handle_list(self):
        """Обробка списку об'єктів"""
        if not self.require_auth():
            return
        
        user_objects = self.objects.get_objects_by_owner(self.current_user_id)
        if user_objects:
            print("\nВаші об'єкти:")
            for obj in user_objects:
                print(f"  {obj['name']} ({obj['type']}) - ID: {obj['id']}")
        else:
            print("У вас немає об'єктів")
    
    def handle_take(self, args):
        """Обробка операції take"""
        if not self.require_auth():
            return
        if len(args) < 3:
            print("Використання: take <source_object> <target_object> <rights>")
            print("  rights: r,w,x,t,g,o (через кому)")
            return
        
        source = args[0]
        target = args[1]
        rights_str = args[2]
        
        # Парсинг прав
        rights = set()
        for r in rights_str.split(','):
            r = r.strip().lower()
            if r == 'r':
                rights.add(AccessRight.READ)
            elif r == 'w':
                rights.add(AccessRight.WRITE)
            elif r == 'x':
                rights.add(AccessRight.EXECUTE)
            elif r == 't':
                rights.add(AccessRight.TAKE)
            elif r == 'g':
                rights.add(AccessRight.GRANT)
            elif r == 'o':
                rights.add(AccessRight.OWN)
        
        if self.graph.take(self.current_user_id, source, target, rights):
            print(f"Операція take успішна: отримано права {rights_str} від {source} до {target}")
            self.audit.log_event(EventType.TAKE_OPERATION, self.current_user_id,
                               {'source': source, 'target': target, 'rights': rights_str})
        else:
            print("Помилка: операція take не вдалася")
    
    def handle_grant(self, args):
        """Обробка операції grant"""
        if not self.require_auth():
            return
        if len(args) < 3:
            print("Використання: grant <source_object> <target_subject> <rights>")
            print("  rights: r,w,x,t,g,o (через кому)")
            return
        
        source = args[0]
        target = args[1]
        rights_str = args[2]
        
        # Парсинг прав
        rights = set()
        for r in rights_str.split(','):
            r = r.strip().lower()
            if r == 'r':
                rights.add(AccessRight.READ)
            elif r == 'w':
                rights.add(AccessRight.WRITE)
            elif r == 'x':
                rights.add(AccessRight.EXECUTE)
            elif r == 't':
                rights.add(AccessRight.TAKE)
            elif r == 'g':
                rights.add(AccessRight.GRANT)
            elif r == 'o':
                rights.add(AccessRight.OWN)
        
        if self.graph.grant(self.current_user_id, source, target, rights):
            print(f"Операція grant успішна: надано права {rights_str} від {source} до {target}")
            self.audit.log_event(EventType.GRANT_OPERATION, self.current_user_id,
                               {'source': source, 'target': target, 'rights': rights_str})
        else:
            print("Помилка: операція grant не вдалася")
    
    def handle_check(self, args):
        """Обробка перевірки доступу"""
        if not self.require_auth():
            return
        if len(args) < 2:
            print("Використання: check <object_id> <right>")
            print("  right: r,w,x,t,g,o")
            return
        
        obj_id = args[0]
        right_str = args[1].lower()
        
        right_map = {
            'r': AccessRight.READ,
            'w': AccessRight.WRITE,
            'x': AccessRight.EXECUTE,
            't': AccessRight.TAKE,
            'g': AccessRight.GRANT,
            'o': AccessRight.OWN
        }
        
        if right_str not in right_map:
            print(f"Невідоме право: {right_str}")
            return
        
        right = right_map[right_str]
        if self.security.can_access(self.current_user_id, obj_id, right):
            print(f"Доступ до {obj_id} з правом {right_str} дозволено")
            self.audit.log_event(EventType.ACCESS_GRANTED, self.current_user_id,
                               {'object_id': obj_id, 'right': right_str})
        else:
            print(f"Доступ до {obj_id} з правом {right_str} заборонено")
            self.audit.log_event(EventType.ACCESS_DENIED, self.current_user_id,
                               {'object_id': obj_id, 'right': right_str}, success=False)
    
    def handle_admin(self, args):
        """Обробка адміністративних команд"""
        if not self.require_auth():
            return
        if not self.admin.is_admin(self.current_user_id):
            print("Помилка: ви не маєте прав адміністратора")
            return
        
        if len(args) < 1:
            print("Використання: admin <command>")
            return
        
        cmd = args[0].lower()
        
        if cmd == "list_users":
            users = self.admin.list_all_users(self.current_user_id)
            print("\nКористувачі системи:")
            for user in users:
                is_admin = self.auth.is_admin(user)
                print(f"  {user} {'(адміністратор)' if is_admin else ''}")
        
        elif cmd == "list_objects":
            objs = self.admin.list_all_objects(self.current_user_id)
            print("\nВсі об'єкти:")
            for obj in objs:
                print(f"  {obj['name']} ({obj['type']}) - ID: {obj['id']}, власник: {obj['owner']}")
        
        elif cmd == "matrix":
            matrix = self.admin.get_access_matrix(self.current_user_id)
            print("\nМатриця доступу:")
            for entry in matrix:
                rights_str = ",".join(entry['rights'])
                print(f"  {entry['subject']} -> {entry['object']}: {rights_str}")
        
        elif cmd == "grant":
            if len(args) < 4:
                print("Використання: admin grant <subject> <object> <rights>")
                return
            subject = args[1]
            obj = args[2]
            rights_str = args[3]
            
            rights = set()
            for r in rights_str.split(','):
                r = r.strip().lower()
                if r == 'r':
                    rights.add(AccessRight.READ)
                elif r == 'w':
                    rights.add(AccessRight.WRITE)
                elif r == 'x':
                    rights.add(AccessRight.EXECUTE)
                elif r == 't':
                    rights.add(AccessRight.TAKE)
                elif r == 'g':
                    rights.add(AccessRight.GRANT)
                elif r == 'o':
                    rights.add(AccessRight.OWN)
            
            if self.admin.grant_rights(self.current_user_id, subject, obj, rights):
                print(f"Права {rights_str} надано {subject} до {obj}")
                self.audit.log_event(EventType.ADMIN_ACTION, self.current_user_id,
                                   {'action': 'grant', 'subject': subject, 'object': obj})
            else:
                print("Помилка: не вдалося надати права")
        
        else:
            print(f"Невідома адміністративна команда: {cmd}")
    
    def handle_audit(self, args):
        """Обробка команд аудиту"""
        if not self.require_auth():
            return
        
        if len(args) < 1:
            print("Використання: audit <all|failed|success>")
            return
        
        cmd = args[0].lower()
        
        if cmd == "all":
            events = self.audit.get_all_events()
            print(f"\nВсього подій: {len(events)}")
            for event in events[-20:]:  # Останні 20 подій
                status = "✓" if event['success'] else "✗"
                print(f"  {status} [{event['timestamp']}] {event['type']} - {event['subject']}")
        
        elif cmd == "failed":
            events = self.audit.get_failed_accesses()
            print(f"\nНеуспішні доступи: {len(events)}")
            for event in events:
                print(f"  [{event['timestamp']}] {event['type']} - {event['subject']}")
        
        elif cmd == "success":
            events = self.audit.get_successful_operations()
            print(f"\nУспішні операції: {len(events)}")
            for event in events[-20:]:  # Останні 20 подій
                print(f"  [{event['timestamp']}] {event['type']} - {event['subject']}")
        
        else:
            print(f"Невідома команда аудиту: {cmd}")

