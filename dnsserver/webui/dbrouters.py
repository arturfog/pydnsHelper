class MyDBRouter(object):
    def db_for_read(self, model, **hints):
        # Specify target database with field in_db in model's Meta class
        if model.__name__ == 'Stats':
            return 'stats'
        if model.__name__ == 'ClientIP':
            return 'stats'
        if model.__name__ == 'StatsHosts':
            return 'stats'
        return 'default'

    def db_for_write(self, model, **hints):
        # Specify target database with field in_db in model's Meta class
        if model.__name__ == 'Stats':
            return 'stats'
        if model.__name__ == 'ClientIP':
            return 'stats'
        if model.__name__ == 'StatsHosts':
            return 'stats'
        return 'default'
    
    def allow_syncdb(self, db, model):      
        # Specify target database with field in_db in model's Meta class
        if db == 'stats':
            return False
        else:
            return True
