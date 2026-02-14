import streamlit as st
from src.ssh_login import try_ssh_login, collect_system_utilization


def main() -> None:
    st.set_page_config(page_title="Agentic AI – SSH Login Tester", page_icon="🤖")
    st.title("🤖 Agentic AI – SSH Login Tester")
    st.caption(
        "Enter remote host, username and password. "
        "The app will try an SSH connection and, if successful, can also show "
        "system utilisation of the remote machine."
    )

    # ----- INPUTS ----------------------------------------------------
    host = st.text_input("Remote host (IP or DNS name)", placeholder="e.g. 192.168.1.42")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    port = st.number_input("SSH port", min_value=1, max_value=65535, value=22, step=1)

    # ----- TEST LOGIN ------------------------------------------------
    if st.button("Test login"):
        if not host or not username or not password:
            st.error("Please fill in *all* fields before testing.")
        else:
            with st.spinner("Connecting…"):
                success, msg = try_ssh_login(host, username, password, port=port)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    # ----- SHOW UTILISATION -------------------------------------------
    if st.button("Show remote system utilisation"):
        if not host or not username or not password:
            st.error("Please fill in *all* fields before fetching utilisation.")
        else:
            with st.spinner("Connecting and gathering data…"):
                success, data = collect_system_utilization(host, username, password, port=port)

            if not success:
                st.error(data.get("error", "Unknown error"))
                return

            for section, payload in data.items():
                with st.expander(section.upper(), expanded=False):
                    if "error" in payload:
                        st.error(payload["error"])
                    else:
                        st.code(payload["output"], language="text")

    st.markdown("---")
    st.caption(
        "⚠️  **Responsible use only** – run this against systems you own "
        "or for which you have explicit permission. Passwords are never stored."
    )


if __name__ == "__main__":
    main()