-- FreightGPT UAE - Initial Database Schema
-- PostgreSQL 16 Migration

BEGIN;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
CREATE TYPE user_role AS ENUM ('super_admin', 'tenant_admin', 'operations', 'dispatcher', 'sales', 'finance', 'driver', 'shipper', 'viewer');
CREATE TYPE load_status AS ENUM ('pending', 'available', 'bidding', 'booked', 'in_transit', 'delivered', 'cancelled', 'completed');
CREATE TYPE load_type AS ENUM ('ftl', 'ltl', 'partial');
CREATE TYPE truck_type AS ENUM ('trailer', 'flatbed', 'reefer', 'tanker', 'box_truck', 'container', 'lowbed', 'tipper');
CREATE TYPE truck_status AS ENUM ('available', 'in_transit', 'loading', 'maintenance', 'out_of_service', 'reserved');
CREATE TYPE invoice_status AS ENUM ('draft', 'sent', 'viewed', 'overdue', 'paid', 'cancelled', 'refunded');
CREATE TYPE payment_method AS ENUM ('bank_transfer', 'card', 'stripe', 'cash', 'cheque', 'factoring');
CREATE TYPE document_type AS ENUM ('pod', 'bol', 'invoice', 'contract', 'customs', 'license', 'insurance', 'permit', 'other');
CREATE TYPE document_status AS ENUM ('uploaded', 'processing', 'extracted', 'verified', 'rejected', 'archived');
CREATE TYPE comm_channel AS ENUM ('email', 'whatsapp', 'sms', 'voice', 'in_app', 'telegram');
CREATE TYPE comm_direction AS ENUM ('outbound', 'inbound');
CREATE TYPE comm_status AS ENUM ('pending', 'sent', 'delivered', 'read', 'failed', 'bounced');

-- Tenants
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    logo_url VARCHAR(512),
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'viewer',
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Loads
CREATE TABLE loads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    shipper_id UUID REFERENCES users(id),
    external_id VARCHAR(255),
    source VARCHAR(100),
    status load_status DEFAULT 'pending',
    load_type load_type DEFAULT 'ftl',
    origin_city VARCHAR(255) NOT NULL,
    origin_region VARCHAR(100),
    origin_lat NUMERIC(10,7),
    origin_lng NUMERIC(10,7),
    destination_city VARCHAR(255) NOT NULL,
    destination_region VARCHAR(100),
    destination_lat NUMERIC(10,7),
    destination_lng NUMERIC(10,7),
    pickup_date TIMESTAMPTZ NOT NULL,
    delivery_date TIMESTAMPTZ,
    pickup_window_start TIMESTAMPTZ,
    pickup_window_end TIMESTAMPTZ,
    weight_kg NUMERIC(10,2),
    volume_m3 NUMERIC(10,2),
    pallets INT,
    description TEXT,
    commodity VARCHAR(255),
    equipment_type VARCHAR(100),
    temperature_required BOOLEAN DEFAULT false,
    temperature_min_c NUMERIC(5,1),
    temperature_max_c NUMERIC(5,1),
    shipper_rate NUMERIC(12,2),
    carrier_rate NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'AED',
    distance_km NUMERIC(10,2),
    special_instructions TEXT,
    documents_required JSONB DEFAULT '[]',
    is_hazardous BOOLEAN DEFAULT false,
    assigned_truck_id UUID REFERENCES trucks(id),
    assigned_driver_id UUID REFERENCES drivers(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bids
CREATE TABLE bids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    load_id UUID NOT NULL REFERENCES loads(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    amount NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    bid_type VARCHAR(50),
    is_winning BOOLEAN DEFAULT false,
    status VARCHAR(50) DEFAULT 'pending',
    profit_margin NUMERIC(5,2),
    confidence_score NUMERIC(5,2),
    notes TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trucks
CREATE TABLE trucks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    plate_number VARCHAR(50) NOT NULL,
    truck_type truck_type NOT NULL,
    make VARCHAR(100),
    model VARCHAR(100),
    year INT,
    vin VARCHAR(50),
    capacity_kg NUMERIC(10,2),
    capacity_m3 NUMERIC(10,2),
    fuel_type VARCHAR(50),
    fuel_consumption_per_km NUMERIC(6,3),
    status truck_status DEFAULT 'available',
    gps_device_id VARCHAR(100),
    gps_provider VARCHAR(100),
    insurance_policy VARCHAR(255),
    insurance_expiry DATE,
    registration_expiry DATE,
    is_active BOOLEAN DEFAULT true,
    current_lat NUMERIC(10,7),
    current_lng NUMERIC(10,7),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Drivers
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    truck_id UUID REFERENCES trucks(id),
    user_id UUID REFERENCES users(id),
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    license_number VARCHAR(100) NOT NULL,
    license_expiry DATE,
    visa_expiry DATE,
    passport_number VARCHAR(50),
    nationality VARCHAR(100),
    languages JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'available',
    rating NUMERIC(3,2) DEFAULT 5.0,
    total_trips INT DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    load_id UUID REFERENCES loads(id),
    user_id UUID REFERENCES users(id),
    document_type document_type NOT NULL,
    status document_status DEFAULT 'uploaded',
    filename VARCHAR(512) NOT NULL,
    original_filename VARCHAR(512) NOT NULL,
    file_size_bytes INT,
    mime_type VARCHAR(100),
    s3_key VARCHAR(1024),
    ocr_text TEXT,
    extraction JSONB DEFAULT '{}',
    verification_status VARCHAR(50),
    verified_by UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    load_id UUID REFERENCES loads(id),
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    status invoice_status DEFAULT 'draft',
    amount NUMERIC(12,2) NOT NULL,
    tax_amount NUMERIC(12,2) DEFAULT 0,
    total_amount NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    due_date DATE NOT NULL,
    issued_date DATE DEFAULT CURRENT_DATE,
    paid_date DATE,
    payment_terms VARCHAR(100) DEFAULT 'net_30',
    notes TEXT,
    line_items JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Runs
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    agent_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error TEXT,
    duration_ms INT,
    model_used VARCHAR(100),
    tokens_used INT,
    cost FLOAT,
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Communications
CREATE TABLE communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    conversation_id UUID REFERENCES conversations(id),
    channel comm_channel NOT NULL,
    direction comm_direction DEFAULT 'outbound',
    status comm_status DEFAULT 'pending',
    subject VARCHAR(512),
    body TEXT,
    sender VARCHAR(255) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    template_id UUID REFERENCES templates(id),
    external_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_loads_tenant ON loads(tenant_id);
CREATE INDEX idx_loads_status ON loads(status);
CREATE INDEX idx_loads_pickup ON loads(pickup_date);
CREATE INDEX idx_trucks_tenant ON trucks(tenant_id);
CREATE INDEX idx_trucks_status ON trucks(status);
CREATE INDEX idx_drivers_tenant ON drivers(tenant_id);
CREATE INDEX idx_documents_tenant ON documents(tenant_id);
CREATE INDEX idx_documents_load ON documents(load_id);
CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_agent_runs_tenant ON agent_runs(tenant_id);
CREATE INDEX idx_agent_runs_type ON agent_runs(agent_type);
CREATE INDEX idx_communications_tenant ON communications(tenant_id);
CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

COMMIT;
