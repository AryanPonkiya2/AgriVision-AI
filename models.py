import os
import json
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())[:12])
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 1 User has many ScanHistory records
    scans = db.relationship('ScanHistory', backref='user', lazy=True, cascade="all, delete-orphan", order_by="desc(ScanHistory.created_at)")

    def __getitem__(self, key):
        """Allow subscript access like user['first_name'] for backward compatibility."""
        return getattr(self, key)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class ScanHistory(db.Model):
    __tablename__ = 'scan_history'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    plant_type = db.Column(db.String(100), nullable=False)
    disease_name = db.Column(db.String(150), nullable=False)
    confidence = db.Column(db.Float, nullable=False, default=0.0)
    scan_type = db.Column(db.String(50), default='plant')
    cause = db.Column(db.Text, nullable=True)
    prevention = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.String(100), nullable=False, default=lambda: datetime.now().strftime("%b %d, %Y - %I:%M %p"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __getitem__(self, key):
        """Allow subscript access like item['filename'] for backward compatibility."""
        return getattr(self, key)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'plant_type': self.plant_type,
            'disease_name': self.disease_name,
            'confidence': self.confidence,
            'scan_type': self.scan_type,
            'cause': self.cause or "",
            'prevention': self.prevention or "",
            'treatment': self.treatment or "",
            'timestamp': self.timestamp
        }


def migrate_from_json(base_dir, upload_folder):
    """
    Automatically migrates existing records from users.json and scan_history.json
    into SQLite if the tables are currently empty.
    """
    users_file = os.path.join(base_dir, 'users.json')
    history_file = os.path.join(upload_folder, 'scan_history.json')

    # 1. Migrate Users
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                raw_users = json.load(f)
            
            for u in raw_users:
                existing = User.query.filter_by(email=u.get('email', '').strip().lower()).first()
                if not existing and u.get('email') and u.get('password_hash'):
                    user = User(
                        id=u.get('id', str(uuid.uuid4())[:12]),
                        first_name=u.get('first_name', 'User'),
                        last_name=u.get('last_name', ''),
                        email=u.get('email', '').strip().lower(),
                        password_hash=u.get('password_hash'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(user)
            db.session.commit()
            print("Successfully migrated users from users.json to database.")
        except Exception as e:
            db.session.rollback()
            print(f"User migration notice: {e}")

    # 2. Migrate Scan History
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                raw_history = json.load(f)

            for item in raw_history:
                existing_scan = ScanHistory.query.filter_by(id=item.get('id')).first()
                if not existing_scan and item.get('filename'):
                    scan = ScanHistory(
                        id=item.get('id', str(uuid.uuid4())[:8]),
                        filename=item.get('filename'),
                        plant_type=item.get('plant_type', 'Unknown'),
                        disease_name=item.get('disease_name', 'Unknown'),
                        confidence=float(item.get('confidence', 0.0)),
                        scan_type=item.get('scan_type', 'plant'),
                        cause=item.get('cause', ''),
                        prevention=item.get('prevention', ''),
                        treatment=item.get('treatment', ''),
                        timestamp=item.get('timestamp') or datetime.now().strftime("%b %d, %Y - %I:%M %p"),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(scan)
            db.session.commit()
            print("Successfully migrated scan history from scan_history.json to database.")
            # Rename legacy file so it does not resurrect deleted records on restarts
            try:
                migrated_file = history_file + '.migrated'
                if os.path.exists(migrated_file):
                    os.remove(migrated_file)
                os.rename(history_file, migrated_file)
            except Exception:
                pass
        except Exception as e:
            db.session.rollback()
            print(f"Scan history migration notice: {e}")
