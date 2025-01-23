import streamlit as st
import pandas as pd
import io

def compare_csvs(source_df, target_df):
    """Compares two DataFrames and highlights added rows."""

    merged_df = pd.merge(source_df, target_df, how='left', indicator='SourceOnly')
    added_rows = merged_df[merged_df['SourceOnly'] == 'left_only'].drop(columns='SourceOnly')
    num_added_rows = len(added_rows)
    return added_rows, num_added_rows

def display_dataframe(df, added_rows=None, key=None): # Added key parameter
    """Displays a DataFrame with highlighted rows and makes it editable."""

    if added_rows is not None and not added_rows.empty:
        def highlight_rows(row):
            if tuple(row.values) in [tuple(r) for r in added_rows.values]:
                return ['background-color: lightcoral'] * len(row)
            return [''] * len(row)

        edited_df = st.data_editor(df.style.apply(highlight_rows, axis=1), use_container_width=True, key=key) # Added key
        return edited_df
    else:
        edited_df = st.data_editor(df, use_container_width=True, key=key) # Added key
        return edited_df

st.title("CSV Comparison Tool")

source_file = st.file_uploader("Upload Source CSV", type=["csv"])
target_file = st.file_uploader("Upload Target CSV", type=["csv"])

if source_file and target_file:
    try:
        source_df = pd.read_csv(source_file)
        target_df = pd.read_csv(target_file)

        if not source_df.columns.equals(target_df.columns):
            st.error("Error: CSV files must have the same columns.")
        else:
            added_rows, num_added_rows = compare_csvs(source_df, target_df)

            st.subheader("Target Data:")
            edited_target_df = display_dataframe(target_df, key="target_df") # Added key

            if num_added_rows > 0:
                st.subheader(f"Added Rows in Source (Not in Target): {num_added_rows} rows")
                edited_added_rows = display_dataframe(added_rows, added_rows, key="added_rows") # Added key

            else:
                st.info("No additional rows found in the source file.")
            
            #Download edited target data
            if st.download_button(
                label="Download edited target data as CSV",
                data=edited_target_df.to_csv().encode('utf-8'),
                file_name='edited_target.csv',
                mime='text/csv',
            ):
                st.write('download complete!')
            
            #Download edited added rows data
            if num_added_rows > 0:
                if st.download_button(
                    label="Download edited added rows data as CSV",
                    data=edited_added_rows.to_csv().encode('utf-8'),
                    file_name='edited_added_rows.csv',
                    mime='text/csv',
                ):
                    st.write('download complete!')

    except pd.errors.ParserError:
        st.error("Error: Invalid CSV file format.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
