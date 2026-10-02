import ipaddress

from sqlalchemy import Table, select

from .database import engine, Base


class Printer(Base):
    __tablename__ = "printers"
    __table__ = Table(__tablename__, Base.metadata, autoload_with=engine)

    
    def __repr__(self) -> str:
        return f"Printer(num_serial='{self.num_serial}', model='{self.model}', status='{self.status}', ip='{self.ip}', counter='{self.counter}', function='{self.printer_function}', last_modify='{self.last_modify}')"
    
    
    @classmethod
    def get_all(cls, session):
        stmt = select(cls).where(cls.active.is_(True))
        return session.scalars(stmt).all()


    @classmethod
    def get_by_serial(cls, printer_serial, session):
        stmt = select(cls).where(
            cls.active.is_(True)
            ,cls.num_serial == printer_serial
        )
        return session.execute(stmt).scalar_one_or_none()
    

class Branch(Base):
    __tablename__ = "branches"
    __table__ = Table(__tablename__, Base.metadata, autoload_with=engine)
    
    
    def __repr__(self) -> str:
        return f"Branch(Id='{str(self.id)}', Name='{self.name}')"
        
    
    @classmethod
    def get_all(cls, session):
        stmt = select(cls)
        return session.scalars(stmt).all()


    @classmethod
    def get_by_branch_id(cls, branch_id, session):
        stmt = select(cls).where(
            cls.id == branch_id
        )
        return session.execute(stmt).scalar_one_or_none()
    
    
    @classmethod
    def get
    
    
    
class BranchNetwork(Base):
    __tablename__ = "branch_networks"
    __table__ = Table(__tablename__, Base.metadata, autoload_with=engine)
    
    def _bytes_to_ip(self, b_data: bytes) -> str:
        """Converte BINARY(16) para string de IP respeitando a versão."""

        if not b_data:
            return ""

        version = (
            str(self.ip_version)
        )

        if version == 'ipv4':
            return str(ipaddress.IPv4Address(b_data[:4]))

        if version == 'ipv6':
            return str(ipaddress.IPv6Address(b_data[:16]))

        raise ValueError(
            f"Versão IP inválida: {self.ip_version!r}"
        )


    @property
    def start_readable(self) -> str:
        return self._bytes_to_ip(self.ip_start)

    @property
    def end_readable(self) -> str:
        return self._bytes_to_ip(self.ip_end)
    
    
    def __repr__(self) -> str:
        return f"Network(Id='{str(self.id)}', Branch_id='{self.branch_id}', Ip_start='{self.start_readable}', Ip_end='{self.end_readable}', Descrição='{self.description}', Ativa='{self.active}')"
        
    
    @classmethod
    def get_all(cls, session):
        stmt = select(cls).where(
            cls.active == True
        )
        return session.scalars(stmt).all()


    @classmethod
    def get_by_branch_id(cls, branch_id, session):
        stmt = select(cls).where(
            cls.branch_id == branch_id,
            cls.active == True
        )
        return session.scalars(stmt).all()
    
    
    @classmethod
    def get_by_id(cls, network_id, session):
        stmt = select(cls).where(
            cls.id == network_id,
            cls.active == True
        )
        return session.execute(stmt).scalar_one_or_none()