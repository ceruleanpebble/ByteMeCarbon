"""
Database models for user authentication and history tracking.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to optimization history
    optimizations = db.relationship('OptimizationHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_total_energy_saved(self):
        """Calculate total energy saved across all optimizations."""
        total = sum(opt.energy_saved for opt in self.optimizations if opt.energy_saved)
        return round(total, 6)
    
    def get_total_optimizations(self):
        """Get total number of optimizations performed."""
        return len(self.optimizations)
    
    def __repr__(self):
        return f'<User {self.email}>'


class OptimizationHistory(db.Model):
    """Track optimization history for each user."""
    __tablename__ = 'optimization_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_code = db.Column(db.Text, nullable=False)
    optimized_code = db.Column(db.Text, nullable=False)
    
    # Metrics
    before_complexity = db.Column(db.String(50))
    after_complexity = db.Column(db.String(50))
    time_saved = db.Column(db.Float, default=0.0)
    energy_saved = db.Column(db.Float, default=0.0)  # in kWh
    co2_reduced = db.Column(db.Float, default=0.0)  # in kg
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_code': self.original_code,
            'optimized_code': self.optimized_code,
            'before_complexity': self.before_complexity,
            'after_complexity': self.after_complexity,
            'time_saved': self.time_saved,
            'energy_saved': self.energy_saved,
            'co2_reduced': self.co2_reduced,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<OptimizationHistory {self.filename} - {self.created_at}>'
