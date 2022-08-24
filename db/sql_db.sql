--
-- PostgreSQL database dump
--

-- Dumped from database version 13.8
-- Dumped by pg_dump version 13.8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


--
-- Name: cointracker; Type: DATABASE; Schema: -; Owner: postgres
--



ALTER DATABASE cointracker OWNER TO postgres;

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: syncs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.syncs (
    sync_id bigint NOT NULL,
    user_id bigint NOT NULL,
    added_to_db_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    is_manual boolean DEFAULT false NOT NULL
);


ALTER TABLE public.syncs OWNER TO postgres;

--
-- Name: syncs_sync_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.syncs_sync_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.syncs_sync_id_seq OWNER TO postgres;

--
-- Name: syncs_sync_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.syncs_sync_id_seq OWNED BY public.syncs.sync_id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    tx_id bigint NOT NULL,
    hash_transaction character varying(64) NOT NULL,
    "time" bigint NOT NULL,
    size bigint NOT NULL,
    weight bigint NOT NULL,
    fee bigint NOT NULL
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: transactions_in_out; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions_in_out (
    address character varying(64) NOT NULL,
    value bigint NOT NULL,
    tx_in_out_id bigint NOT NULL,
    is_input boolean NOT NULL,
    added_to_db_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tx_id bigint NOT NULL
);


ALTER TABLE public.transactions_in_out OWNER TO postgres;

--
-- Name: transactions_in_out_tx_in_out_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_in_out_tx_in_out_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_in_out_tx_in_out_id_seq OWNER TO postgres;

--
-- Name: transactions_in_out_tx_in_out_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_in_out_tx_in_out_id_seq OWNED BY public.transactions_in_out.tx_in_out_id;


--
-- Name: transactions_tx_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_tx_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_tx_id_seq OWNER TO postgres;

--
-- Name: transactions_tx_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_tx_id_seq OWNED BY public.transactions.tx_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id bigint NOT NULL,
    added_to_db_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: users_wallets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_wallets (
    user_id bigint NOT NULL,
    wallet_id bigint NOT NULL,
    added_to_db_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.users_wallets OWNER TO postgres;

--
-- Name: wallets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wallets (
    wallet_id bigint NOT NULL,
    address character varying(64) NOT NULL,
    n_tx bigint,
    total_received bigint,
    total_sent bigint,
    final_balance bigint,
    last_scan_at timestamp with time zone,
    added_to_db_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ongoing_scan boolean
);


ALTER TABLE public.wallets OWNER TO postgres;

--
-- Name: wallets_wallet_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.wallets_wallet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wallets_wallet_id_seq OWNER TO postgres;

--
-- Name: wallets_wallet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.wallets_wallet_id_seq OWNED BY public.wallets.wallet_id;


--
-- Name: syncs sync_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.syncs ALTER COLUMN sync_id SET DEFAULT nextval('public.syncs_sync_id_seq'::regclass);


--
-- Name: transactions tx_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN tx_id SET DEFAULT nextval('public.transactions_tx_id_seq'::regclass);


--
-- Name: transactions_in_out tx_in_out_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions_in_out ALTER COLUMN tx_in_out_id SET DEFAULT nextval('public.transactions_in_out_tx_in_out_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: wallets wallet_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallets ALTER COLUMN wallet_id SET DEFAULT nextval('public.wallets_wallet_id_seq'::regclass);


--
-- Name: syncs syncs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.syncs
    ADD CONSTRAINT syncs_pkey PRIMARY KEY (sync_id);


--
-- Name: transactions transactions_hash_transaction_tx_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_hash_transaction_tx_id_key UNIQUE (hash_transaction) INCLUDE (tx_id);


--
-- Name: transactions_in_out transactions_in_out_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions_in_out
    ADD CONSTRAINT transactions_in_out_pkey PRIMARY KEY (tx_in_out_id, address, value);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (tx_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users_wallets users_wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_wallets
    ADD CONSTRAINT users_wallets_pkey PRIMARY KEY (user_id, wallet_id);


--
-- Name: wallets wallets_address_wallet_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_address_wallet_id_key UNIQUE (address) INCLUDE (wallet_id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (wallet_id);


--
-- Name: transactions_in_out_address_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transactions_in_out_address_idx ON public.transactions_in_out USING btree (address) INCLUDE (tx_id);


--
-- Name: transactions_in_out transactions_in_out_tx_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions_in_out
    ADD CONSTRAINT transactions_in_out_tx_id_fkey FOREIGN KEY (tx_id) REFERENCES public.transactions(tx_id);


--
-- Name: users_wallets users_wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_wallets
    ADD CONSTRAINT users_wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: users_wallets users_wallets_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_wallets
    ADD CONSTRAINT users_wallets_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES public.wallets(wallet_id);
--
-- PostgreSQL database dump complete
--
